from fastapi import (FastAPI, status, Request, Form, Depends, BackgroundTasks,
                     HTTPException)
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi_login import LoginManager

# Set up user authentication flows
from passlib.context import CryptContext
from datetime import timedelta, datetime
from typing import Optional
import urllib.parse
import pendulum
import os
import re

# My own packages
import process
import nlb_rest_api
import m_db


# Load environment variables
SECRET_KEY = os.environ["mongo_secret_key"]
ACCESS_TOKEN_EXPIRY = 60

APPLICATION_ID = os.environ['nlb_rest_app_id']
API_KEY = os.environ['nlb_rest_api_key']

manager = LoginManager(SECRET_KEY, token_url="/login", use_cookie=True)
manager.cookie_name = "auth"


def get_db():
    db = m_db.connect_mdb()
    db_nlb = db['nlb']
    return db_nlb


# Password hashing setup
pwd_ctx = CryptContext(schemes=['bcrypt'], deprecated="auto")


def get_hashed_password(plain_password):
    return pwd_ctx.hash(plain_password)


def verify_password(plain_password, hashed_password):
    return pwd_ctx.verify(plain_password, hashed_password)


@manager.user_loader()
def get_user(username: str):

    db = m_db.connect_mdb()
    db_nlb = db['nlb']
    user = m_db.mg_query_user_by_username(db=db_nlb, username=username)
    if user:
        return user


def authenticate_user(username: str,
                      password: str,
                      db=Depends(get_db)):
    user = m_db.mg_query_user_by_username(db=db, username=username)
    if not user:
        return None
    if not verify_password(plain_password=password,
                           hashed_password=user.get("HashedPassword")):
        return None
    return user


class NotAuthenticationException(Exception):
    pass


def not_authenticated_exception_handler(request, exception):
    return RedirectResponse("/")


# Application code
app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')


manager.not_authenticated_exception = NotAuthenticationException
app.add_exception_handler(NotAuthenticationException,
                          not_authenticated_exception_handler)


# Define an error handler to render the error page
@app.exception_handler(HTTPException)
async def handle_http_exception(request: Request, exc: HTTPException):
    return templates.TemplateResponse("error.html", {"request": request})


# Example route that triggers an internal server error
@app.get("/trigger-error")
def trigger_error():
    raise HTTPException(status_code=500, detail="Internal Server Error")


# Logout
@app.get("/logout")
def logout():
    response = RedirectResponse("/")
    manager.set_cookie(response, None)
    return response


# Register page
@app.get("/register_complete/{username}", response_class=HTMLResponse)
def get_register(request: Request, username: str):

    return templates.TemplateResponse(
        "register_complete.html",
        {"request": request, "username": username})


@app.get("/check_user_register/", response_class=HTMLResponse)
async def check_user_register(username):

    db = m_db.connect_mdb()
    db_nlb = db['nlb']
    user = m_db.mg_query_user_by_username(db=db_nlb, username=username)
    if user:
        dup_user_msg = f"{username} is already registered"

        return f"""<button type="submit" class="bg-gray-400 text-white
                    border-white rounded-lg py-1.5 mt-4 px-3 mx-3
                    disabled:bg-gray-400 disabled:hover:bg-gray-400" disabled
                    >Register</button>
                    <p class="italic py-1.5 mt-4 px-3">{dup_user_msg}</p>
                    """
    else:
        return """<button type="submit"
                class="bg-red-400 text-white border-white
                rounded-lg py-1.5 mt-4 px-3 mx-2">Register</button>"""


@app.post("/")
def register_user(request: Request,
                  username: Optional[str] = Form(...),
                  password: Optional[str] = Form(...),
                  db=Depends(get_db)):

    hashed_password = get_hashed_password(password)
    invalid = False

    if username:
        if m_db.mg_query_user_by_username(db=db, username=username):
            invalid = True

        if not invalid:
            m_db.mg_add_user(db=db, username=username,
                             hashed_pw=hashed_password)

            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRY)
            access_token = manager.create_access_token(
                data={"sub": username},
                expires=access_token_expires)

            resp = RedirectResponse("/register_complete/" +
                                    urllib.parse.quote(username),
                                    status_code=status.HTTP_302_FOUND)

            m_db.mg_event_tracking(db, 'users', username, "registered_time")
            m_db.mg_event_tracking(db, 'users', username, 'latest_login')

            manager.set_cookie(resp, access_token)
            return resp

    else:
        return templates.TemplateResponse(
            "homepage.html",
            {"request": request,
             "register_invalid": True},
            status_code=status.HTTP_400_BAD_REQUEST)


# Base page
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("homepage.html", {"request": request})


# Login
@app.post("/login")
def login(request: Request,
          form_data: OAuth2PasswordRequestForm = Depends(),
          db=Depends(get_db)):

    user = authenticate_user(username=form_data.username,
                             password=form_data.password,
                             db=db)

    if not user:
        return templates.TemplateResponse(
            "homepage.html",
            {"request": request,
             "login_invalid": True},
            status_code=status.HTTP_401_UNAUTHORIZED)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRY)
    access_token = manager.create_access_token(
        data={"sub": user.get("UserName")},
        expires=access_token_expires)

    resp = RedirectResponse(
        f"/{user.get('UserName')}/main/", status_code=status.HTTP_302_FOUND)

    manager.set_cookie(resp, access_token)

    # Track user login
    m_db.mg_event_tracking(db, 'users', user.get("UserName"), 'latest_login')
    return resp


@app.get("/forgot_password", response_class=HTMLResponse)
async def forgot_password(request: Request,
                          wrong_question=False):
    return templates.TemplateResponse("forgot_password.html", {
        "request": request})


@app.get("/reset_password/", response_class=HTMLResponse)
async def reset_password(request: Request,
                         username: str = Form(...),
                         pw_qn: str = Form(...),
                         pw_ans: str = Form(...),
                         new_password: str = Form(...)
                         ):

    db = m_db.connect_mdb()
    db_nlb = db['nlb']

    user = m_db.mg_query_user(db=db_nlb, username=username)
    if user:
        if user.get("pw_qn") == pw_qn & user.get("pw_ans") == pw_ans:
            hashed_password = get_hashed_password(new_password)
            new_dict = {"HashedPassword": hashed_password}
            m_db.mg_update_user_info(db, username.get("UserName"), new_dict)

    else:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User email not found"
        )
    return RedirectResponse("/", status_code=status.HTTP_302_FOUND)


@app.get("/{username}/main")
async def htmx_main(request: Request,
                    db=Depends(get_db),
                    username=Depends(manager)):

    try:
        response = process_user_book_data(
            db=db, username=username.get("UserName"))

        update_status = None
        if m_db.mg_query_status(db=db, username=username.get("UserName")):
            update_status = "Updating In Progress... Please refresh to update!"

        # Processing necessary statistics
        all_unique_books = process.process_all_unique_books(response)
        all_avail_books = process.process_all_avail_books(response)
        all_unique_lib = process.process_all_unique_lib(response)
        all_avail_bks_by_lib = process.process_all_avail_bks_by_lib(response)
        lib_book_summary = process.process_lib_book_summary(
            all_unique_lib, all_avail_bks_by_lib)

        update_status = None
        if m_db.mg_query_status(db=db, username=username.get("UserName")):
            update_status = "Updating In Progress!"

        # Check if user has a default library
        user_info = m_db.mg_query_user_info(db, username.get("UserName"))
        preferred_lib = user_info.get("preferred_lib")

        if preferred_lib:
            preferred_lib = preferred_lib.lower()
            output = []
            for book in response:
                if preferred_lib in book['BranchName'].lower():
                    output.append(book)

        else:
            preferred_lib = 'all'
            output = response

        lib_avail = len(process.process_all_avail_books(output))
        lib_all = len(process.process_all_unique_books(output))

        return templates.TemplateResponse("main.html", {
            "request": request,
            "username": username.get("UserName"),
            "api_data": output,
            'all_avail_books': all_avail_books,
            'all_unique_books': all_unique_books,
            'avail_books': all_avail_bks_by_lib,
            'lib_book_summary': lib_book_summary,
            'lib_avail': lib_avail,
            'lib_all': lib_all,
            "library": preferred_lib,
            "status": update_status
        })

    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/{username}/m_yourbooks")
async def m_current_books(request: Request,
                          db=Depends(get_db),
                          username=Depends(manager)):

    """ Used by htmx to render user books within main_content <div> """

    try:
        update_status = None
        if m_db.mg_query_status(db=db, username=username.get("UserName")):
            update_status = "Updating In Progress... Please refresh to update!"

        output = []
        if username:
            # Get all the books linked to the user.
            # This is the complicated query
            query = m_db.mg_query_user_bookmarked_books(
                db=db, username=username.get("UserName"))

            response = []
            for a in query:
                response.append({
                    "TitleName": a.get('TitleName').split("/")[0].strip(),
                    "BID": a.get("BID"),
                    "CallNumber": a.get("CallNumber").split(" -")[0].strip()})

                result = list({d['TitleName']: d for d in response}.values())

                output = []
                for r in result:
                    output.append({
                        "CallNumber": r.get('CallNumber'),
                        "TitleName": r.get('TitleName') + ' | ' + r.get("BID"),
                        "BID": r.get("BID")
                    })

            return templates.TemplateResponse("m_yourbooks.html", {
                "request": request,
                "username": username.get("UserName"),
                "api_data": output,
                "status": update_status
            })
        else:
            return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")


def process_user_book_data(db, username: str):
    """ Process db result for frontpage """

    query = m_db.mg_query_user_bookmarked_books(db=db, username=username)
    response = []

    for a in query:
        if a.get("DueDate"):
            tmp_date = a.get("DueDate").split("T")[0]

            try:
                input_date = datetime.strptime(tmp_date, "%Y-%m-%d")

            except Exception:
                input_date = datetime.strptime(tmp_date, "%d/%m/%Y")

            due_date = input_date.strftime("%d/%m")

        else:
            due_date = None

        update_time = datetime.fromtimestamp(
            a.get("InsertTime"), pendulum.timezone("Asia/Singapore")
        ).strftime("%d/%m %H:%M")

        if "Not" in a.get("StatusDesc"):
            status = "Available"
        elif "Loan" in a.get("StatusDesc"):
            status = "Loan"
        elif "Transit" in a.get("StatusDesc"):
            status = "Transit"
        elif "Reference" in a.get("StatusDesc"):
            status = "Reference"
        else:
            status = a.get("StatusDesc")

        if due_date is None:
            final_status = status
        else:
            final_status = status + '[' + str(due_date) + ']'

        if "Lifelong Learning" in a.get("BranchName"):
            library = "Lifelong Learning Institute"
        elif "Public Library" in a.get("BranchName"):
            library = a.get("BranchName").split("Public Library")[0]
        elif "Library" in a.get("BranchName"):
            library = a.get("BranchName").split("Library")[0]
        else:
            library = a.get("BranchName")

        response.append({
            "TitleName": a.get('TitleName'
                               ).split("/")[0] + ' | ' + a.get("BID"),
            "BranchName": library,
            "CallNumber": a.get("CallNumber").split(" -")[0],
            "StatusDesc": final_status,
            "UpdateTime": update_time,
            "BID": a.get("BID")})

    return response


@app.get("/{username}/m_lib/{library}/", response_class=HTMLResponse)
async def show_avail_m_books(request: Request,
                             library: Optional[str],
                             db=Depends(get_db),
                             username=Depends(manager)):
    try:
        if username:
            response = process_user_book_data(
                db=db, username=username.get("UserName"))

            all_unique_books = process.process_all_unique_books(response)
            all_avail_books = process.process_all_avail_books(response)

            update_status = None
            if m_db.mg_query_status(db=db, username=username.get("UserName")):
                update_status = "Updating In Progress!"

            if library != 'all':
                output = []
                for book in response:
                    if library in book['BranchName'].lower():
                        output.append(book)
            else:
                output = response

            lib_avail = len(process.process_all_avail_books(output))
            lib_all = len(process.process_all_unique_books(output))

            return templates.TemplateResponse("m_result.html", {
                "request": request,
                "username": username.get("UserName"),
                "api_data": output,
                'library': library,
                'all_avail_books': all_avail_books,
                'all_unique_books': all_unique_books,
                'lib_avail': lib_avail,
                'lib_all': lib_all,
                'status': update_status
            })

        else:
            return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")


def update_bk_avail_in_mongo(db, bid_no):
    """ This function does four things
    1. Make API calls to NLB to get book availability
    2. Process and combine the records into a single List[Dict]
    3. Delete existing book available records in MongoDB
    4. Ingest new book available records into MongoDB

    """
    try:
        # Make API call on book availability
        bk = nlb_rest_api.get_rest_nlb_api_v2(
            "GetAvailabilityInfo", input=bid_no)

        all_books_avail = nlb_rest_api.process_rest_all_lib_avail_v2(bk)

        if len(all_books_avail) > 0:
            # Delete existing MongoDB records
            m_db.mg_delete_bk_avail_records(db=db, bid_no=bid_no)

            # Add new records into MongoDB
            m_db.mg_add_entire_book_avail(db=db, books_avail=all_books_avail)

            return {"API call": True}

        else:
            # Something wrong with the NLB API and nothing is updated...
            return {"API call": False}

    except Exception:
        return {"API call": False}


def bk_info_api_call_n_db_ingest(db, bid_no):
    # Make API calls to book info and ingest into DB

    book_title_rest_api = nlb_rest_api.get_rest_nlb_api_v2(
        "GetTitleDetails", input=bid_no)
    book_title = nlb_rest_api.process_rest_bk_info(book_title_rest_api)
    book_title.update({"BID": str(bid_no)})

    # Consider keeping this so that I can show this as well
    del book_title['PublishYear']

    # Need to clear up my title names now
    book_title['TitleName'] = book_title['TitleName'].split("/")[0]

    m_db.mg_add_book_info(db=db, books_info_input=book_title)


@app.post("/update_book/{BID}", response_class=HTMLResponse)
async def update_book(BID: str,
                      db=Depends(get_db),
                      username=Depends(manager)):

    api_result = update_bk_avail_in_mongo(db, BID)

    if api_result.get("API call"):
        return RedirectResponse(f"/{username.get('UserName')}/main",
                                status_code=status.HTTP_302_FOUND)


def update_all_user_books(db, username):
    """ Update all books linked to user. No NLB password needed """

    user_bids = m_db.mg_query_user_books_w_bid(
        db=db, username=username.get("UserName"))

    m_db.mg_insert_status(db, username=username.get("UserName"))

    if user_bids:
        for ubid in user_bids:
            bid_no = ubid.get("BID")
            update_bk_avail_in_mongo(db, bid_no)

    m_db.mg_delete_status(db, username=username.get("UserName"))

    return {"message": "All user books are updated!"}


@app.post("/m_update_user_books/{username}", response_class=HTMLResponse)
async def m_update_user_current_books(background_tasks: BackgroundTasks,
                                      db=Depends(get_db),
                                      username=Depends(manager)):
    """ Updates availability of all user's saved books """
    background_tasks.add_task(update_all_user_books, db, username)
    return RedirectResponse(f"/{username.get('UserName')}/m_lib/all",
                            status_code=status.HTTP_302_FOUND)


@app.post("/ingest_books", response_class=HTMLResponse)
async def ingest_books(bids: list = Form(...),
                       db=Depends(get_db),
                       username=Depends(manager)):

    for bid in bids:
        BID = str(bid)
        # Makes API to bk info and bk avail and ingest the data into DB
        m_db.mg_add_user_book(db=db,
                              username=username.get("UserName"),
                              bid_no=BID)

        bk_info_api_call_n_db_ingest(db=db, bid_no=BID)
        update_bk_avail_in_mongo(db, BID)

    return RedirectResponse(
        f"/{username.get('UserName')}/main",
        status_code=status.HTTP_302_FOUND)


@app.post("/ingest_books_v2", response_class=HTMLResponse)
async def ingest_books_stay(bids: list = Form(...),
                            db=Depends(get_db),
                            username=Depends(manager)):

    # WIP - I want to change it such that my
    # page will ingest and remain in the original page

    return RedirectResponse(
        f"/{username.get('UserName')}/main",
        status_code=status.HTTP_302_FOUND)


@app.post("/delete_books", response_class=HTMLResponse)
async def delete_books(bids: list = Form(...),
                       db=Depends(get_db),
                       username=Depends(manager)):
    for bid in bids:
        BID = str(bid)
        # Check BID is linked to more than 1 user
        counter = db.user_books.aggregate([
            {"$match": {"BID": BID}},
            {"$group": {"_id": 0, "BID": {"$sum": 1}}},
            {"$project": {"_id": 0}}
        ])
        final_count = counter.next().get("BID")

        # If book is only linked to one user,
        # delete book available and info records
        if final_count == 1:
            m_db.mg_delete_bk_avail_records(db=db, bid_no=BID)
            m_db.mg_delete_bk_info_records(db=db, bid_no=BID)

        m_db.mg_delete_bk_user_records(
            db=db, username=username.get("UserName"), bid_no=BID)

    # WIP - To include code to recalculate the book count
    # And then render the new template

    return RedirectResponse(f"/{username.get('UserName')}/main",
                            status_code=status.HTTP_302_FOUND)


@app.get("/htmx_search", response_class=HTMLResponse)
async def htmx_search_books(request: Request,
                            book_search: Optional[str] = None,
                            author: Optional[str] = None,
                            db=Depends(get_db),
                            username=Depends(manager)):

    """ Calls NLB Search API and pushes the results as a search_table.html"""

    final_response = list()
    search_input = dict()

    if book_search:
        c_book_search = re.sub(r'[^a-zA-Z0-9\s]', ' ', book_search)
        search_input.update({"Title": c_book_search})

    if author:
        c_author = re.sub(r'[^a-zA-Z0-9\s]', ' ', author)
        search_input.update({"Author": c_author})

    if book_search or author:
        titles = nlb_rest_api.get_rest_title(input_dict=search_input)

        search_params = dict()
        search_params['title'] = book_search
        search_params['author'] = author

        m_db.mg_user_search_tracking(db,
                                     table="user_search",
                                     username=username.get("UserName"),
                                     search_params=search_params)

        bad_result = templates.TemplateResponse("search_table.html", {
            "request": request,
            "keyword": book_search,
            "author": author,
            "username": username.get("UserName"),
            "api_data": final_response,
        })

        elist = [400, 404, 500, 401, 405, 429]

        if titles.get("statusCode") in elist:
            return bad_result

        elif titles.get("totalRecords") == 0:
            return bad_result

        else:
            all_titles = nlb_rest_api.get_title_process(titles)

            if titles.get("hasMoreRecords"):
                try:
                    for offset in [20, 40, 60, 80, 100, 120, 140]:
                        titles = nlb_rest_api.get_rest_title(
                            input_dict=search_input, offset=offset)
                        all_titles += nlb_rest_api.get_title_process(
                            titles)
                except Exception:
                    pass

            # Only keep physical books for now
            books_only = []
            for title in all_titles:
                if title['type'] == "Book":
                    books_only.append(title)

            # Search user book BIDs and
            # disable add books for books already saved by user
            user_books = m_db.mg_query_user_bookmarked_books(
                db=db, username=username.get("UserName"))

            user_books_bids = [i.get("BID") for i in user_books]

            for i in books_only:
                try:
                    i['TitleName'] = i['TitleName'].split(
                        " / ")[0].strip() + " | " + str(i['BID'])

                    i['PublishYear'] = "Y" + i['PublishYear']

                    disable = "disabled" if str(
                        i['BID']) in user_books_bids else ""

                    i['BID'] = disable + " | " + str(i["BID"])

                    final_response.append(i)

                except Exception:
                    pass

            print(final_response)

    return templates.TemplateResponse("search_table.html", {
        "request": request,
        "keyword": book_search,
        "author": author,
        "username": username.get("UserName"),
        "api_data": final_response,
    })


@app.get("/{username}/m_search/", response_class=HTMLResponse)
async def m_search_books(request: Request,
                         book_search: Optional[str] = None,
                         author: Optional[str] = None,
                         db=Depends(get_db),
                         username=Depends(manager)):

    update_status = None
    if m_db.mg_query_status(db=db, username=username.get("UserName")):
        update_status = "Updating In Progress!"

    return templates.TemplateResponse("m_search.html", {
        "request": request,
        "keyword": book_search,
        "author": author,
        "username": username.get("UserName"),
        "status": update_status
    })


@app.get("/{username}/m_profile", response_class=HTMLResponse)
async def user_m_profile(request: Request,
                         db=Depends(get_db),
                         username=Depends(manager)):

    response = process_user_book_data(
        db=db, username=username.get("UserName"))

    all_unique_lib = process.process_all_unique_lib(response)

    update_status = None
    if m_db.mg_query_status(db=db, username=username.get("UserName")):
        update_status = "Updating In Progress!"

    # Query user profile info from database
    user_info = m_db.mg_query_user_info(db, username.get("UserName"))
    email_address = user_info.get("email_address")
    preferred_lib = user_info.get("preferred_lib")
    pw_qn = user_info.get("pw_qn")
    pw_ans = user_info.get("pw_ans")

    return templates.TemplateResponse("m_profile.html", {
        "request": request,
        "username": username.get("UserName"),
        "email_address": email_address,
        "preferred_lib": preferred_lib,
        "pw_qn": pw_qn,
        "pw_ans": pw_ans,
        'all_unique_lib': all_unique_lib,
        "status": update_status
    })


@app.post("/update_user/{username}", response_class=HTMLResponse)
async def update_user(request: Request,
                      email_address: str = Form(None),
                      preferred_lib: str = Form(None),
                      pw_qn: str = Form(None),
                      pw_ans: str = Form(None),
                      password: str = Form(None),
                      db=Depends(get_db),
                      username=Depends(manager)):

    # Update info
    new_dict = {'email_address': email_address,
                "preferred_lib": preferred_lib,
                "pw_qn": pw_qn,
                "pw_ans": pw_ans}

    if password:
        hashed_password = get_hashed_password(password)
        new_dict.update({"HashedPassword": hashed_password})

    m_db.mg_update_user_info(db, username.get("UserName"), new_dict)

    return RedirectResponse(f"/profile/{username.get('UserName')}",
                            status_code=status.HTTP_302_FOUND)


@app.post("/delete_user/{username}", response_class=HTMLResponse)
async def delete_user(request: Request,
                      db=Depends(get_db),
                      username=Depends(manager)):

    m_db.mg_delete_user(db, username=username.get("UserName"))
    return RedirectResponse("/logout", status_code=status.HTTP_302_FOUND)


lib_locations = ['Ang Mo Kio Public Library', 'Bedok Public Library',
                 'Bishan Public Library', 'Bukit Panjang Public Library',
                 'Cheng San Public Library', 'Choa Chu Kang Public Library',
                 'Clementi Public Library', 'Geylang East Public Library',
                 'Jurong Regional Library', 'Jurong West Public Library',
                 'National Library', 'Online',
                 'Pasir Ris Public Library', 'Punggol Regional Library',
                 'Queenstown Public Library', 'Sengkang Public Library',
                 'Serangoon Public Library', 'Tampines Regional Library',
                 'The LLiBrary', 'Toa Payoh Public Library',
                 'Woodlands Regional Library', 'Yishun Public Library',
                 'library@chinatown', 'library@harbourfront',
                 'library@orchard']


@app.get("/events", response_class=HTMLResponse)
async def show_events(request: Request,
                      lib: str = "Online",
                      db=Depends(get_db),
                      username=Depends(manager)):

    lib_events = m_db.mg_query_lib_events_by_lib(db, lib)
    today = str(datetime.now().date())

    final_output = list()
    for events in lib_events:
        event_date = events.get('start').split("T")[0]
        if event_date >= today:
            final_output.append(events)

    return templates.TemplateResponse("m_lib_events.html", {
        "request": request,
        "username": username.get("UserName"),
        "lib_events": final_output,
        "total_records": len(final_output),
        'lib_locations': lib_locations,
        "selected_lib": lib
    })


# Functions that are useful for pagination
ITEMS_PER_PAGE = 15


def calculate_total_pages(total_records: int) -> int:
    # Ceiling division to get the total pages
    return -(-total_records // ITEMS_PER_PAGE)


def get_pagination_links(page: int, total_pages: int):
    previous_page = max(page - 1, 1) if page > 1 else None
    next_page = min(page + 1, total_pages) if page < total_pages else None

    return {
        "previous_page": previous_page,
        "next_page": next_page,
        "total_pages": total_pages,
        "current_page": page,
    }


@app.get("/lib_events_base", response_class=HTMLResponse)
async def show_library_events(request: Request,
                              page: int = 1,
                              lib: str = "Online",
                              db=Depends(get_db),
                              username=Depends(manager)):

    lib_events = m_db.mg_query_lib_events_by_lib(db, lib)
    today = str(datetime.now().date())

    final_output = list()
    for events in lib_events:
        event_date = events.get('start').split("T")[0]
        if event_date >= today:
            final_output.append(events)

    start_index = (page - 1) * ITEMS_PER_PAGE
    end_index = start_index + ITEMS_PER_PAGE

    total_records = len(final_output)
    records = final_output[start_index: end_index]
    total_pages = calculate_total_pages(len(final_output))
    pagination_links = get_pagination_links(page, total_pages)

    return templates.TemplateResponse("m_lib_events.html", {
        "request": request,
        "username": username.get("UserName"),
        "lib_events": records,
        "pagination": pagination_links,
        "total_records": total_records,
        'lib_locations': lib_locations,
        "selected_lib": lib
    })


@app.get("/lib_events", response_class=HTMLResponse)
async def show_lib_events(request: Request,
                          lib: str,
                          page: int = 1,
                          db=Depends(get_db),
                          username=Depends(manager)):

    # Filter for online events first
    lib_events = m_db.mg_query_lib_events_by_lib(db, lib)
    today = str(datetime.now().date())

    final_output = list()
    for events in lib_events:
        event_date = events.get('start').split("T")[0]
        if event_date >= today:
            final_output.append(events)

    start_index = (page - 1) * ITEMS_PER_PAGE
    end_index = start_index + ITEMS_PER_PAGE

    total_records = len(final_output)

    records = final_output[start_index: end_index]
    total_pages = calculate_total_pages(len(final_output))
    pagination_links = get_pagination_links(page, total_pages)

    return templates.TemplateResponse("m_lib_events_table.html", {
        "request": request,
        "username": username.get("UserName"),
        "lib_events": records,
        "pagination": pagination_links,
        "total_records": total_records,
        'lib_locations': lib_locations,
        "selected_lib": lib
    })
