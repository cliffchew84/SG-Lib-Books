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

            m_db.mg_event_tracking(db, 'users', username, "registered_time")

            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRY)
            access_token = manager.create_access_token(
                data={"sub": username},
                expires=access_token_expires)

            # resp = RedirectResponse(
            #     f"/{username}", status_code=status.HTTP_302_FOUND)
            # manager.set_cookie(resp, access_token)

            resp = RedirectResponse("/register_complete/" +
                                    urllib.parse.quote(username),
                                    status_code=status.HTTP_302_FOUND)

            manager.set_cookie(resp, access_token)
            return resp

            # return RedirectResponse("/register_complete/" +
            #                        urllib.parse.quote(username),
            #                        status_code=status.HTTP_302_FOUND)

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
             "title": "Login",
             "login_invalid": True},
            status_code=status.HTTP_401_UNAUTHORIZED)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRY)
    access_token = manager.create_access_token(
        data={"sub": user.get("UserName")},
        expires=access_token_expires)

    resp = RedirectResponse(
        f"/{user.get('UserName')}", status_code=status.HTTP_302_FOUND)
    manager.set_cookie(resp, access_token)

    # Track user login
    m_db.mg_event_tracking(db, 'users', user.get("UserName"), 'latest_login')
    return resp


@app.get("/{username}/yourbooks")
async def show_current_books(request: Request,
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

        output = []
        if username:
            # Get all the books linked to the user.
            # This is the complicated query
            query = m_db.mg_query_user_bookmarked_books(
                db=db, username=username.get("UserName"))

            response = []
            for a in query:
                response.append({
                    "TitleName": a.get('TitleName').strip(),
                    "BID": a.get("BID"),
                    "CallNumber": a.get("CallNumber").split(" -")[0].strip()})

                result = list({d['TitleName']: d for d in response}.values())

                i = 0
                output = []
                for r in result:
                    i += 1
                    output.append({
                        "No": "B" + str(i),
                        "CallNumber": r.get('CallNumber'),
                        "TitleName": r.get('TitleName') + ' | ' + r.get("BID"),
                        "BID": r.get("BID")
                    })

            return templates.TemplateResponse("yourbooks.html", {
                "request": request,
                "username": username.get("UserName"),
                "api_data": output,
                'all_unique_books': all_unique_books,
                'all_avail_books': all_avail_books,
                'all_unique_lib': all_unique_lib,
                'avail_books': all_avail_bks_by_lib,
                'lib_book_summary': lib_book_summary,
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

            due_date = input_date.strftime("%d %b")

        else:
            due_date = None

        update_time = datetime.fromtimestamp(
            a.get("InsertTime"), pendulum.timezone("Asia/Singapore")
        ).strftime("%d %b %H:%M")

        if "Not" in a.get("StatusDesc"):
            status = "Available"
        else:
            status = a.get("StatusDesc")

        if due_date is None:
            final_status = status
        else:
            final_status = status + ' [' + str(due_date) + ']'

        if "Lifelong Learning" in a.get("BranchName"):
            library = "Lifelong Learning Institute"
        elif "Public Library" in a.get("BranchName"):
            library = a.get("BranchName").split("Public Library")[0]
        elif "Library" in a.get("BranchName"):
            library = a.get("BranchName").split("Library")[0]
        else:
            library = a.get("BranchName")

        response.append({
            "TitleName": a.get('TitleName') + ' | ' + a.get("BID"),
            "BranchName": library,
            "CallNumber": a.get("CallNumber").split(" -")[0],
            "StatusDesc": final_status,
            "UpdateTime": update_time,
            "BID": a.get("BID")})

    return response


@app.get('/{username}')
async def show_books_avail(request: Request,
                           db=Depends(get_db),
                           username=Depends(manager)):

    try:
        if username:
            response = process_user_book_data(
                db=db, username=username.get("UserName"))

            # Processing necessary statistics
            all_unique_books = process.process_all_unique_books(response)
            all_avail_books = process.process_all_avail_books(response)
            all_unique_lib = process.process_all_unique_lib(response)
            all_avail_bks_by_lib = process.process_all_avail_bks_by_lib(
                response)
            lib_book_summary = process.process_lib_book_summary(
                all_unique_lib, all_avail_bks_by_lib)

            update_status = None
            if m_db.mg_query_status(db=db, username=username.get("UserName")):
                update_status = "Updating In Progress!"

            return templates.TemplateResponse("result.html", {
                "request": request,
                "username": username.get("UserName"),
                "api_data": response,
                'all_unique_books': all_unique_books,
                'all_avail_books': all_avail_books,
                'all_unique_lib': all_unique_lib,
                'avail_books': all_avail_bks_by_lib,
                'lib_book_summary': lib_book_summary,
                'status': update_status
            })
        else:
            return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/{username}/lib/{library}/", response_class=HTMLResponse)
async def show_books_avail_by_lib(request: Request,
                                  library: Optional[str],
                                  db=Depends(get_db),
                                  username=Depends(manager)):

    try:
        if username:
            response = process_user_book_data(
                db=db, username=username.get("UserName"))

            # Processing necessary statistics
            all_unique_books = process.process_all_unique_books(response)
            all_avail_books = process.process_all_avail_books(response)
            all_unique_lib = process.process_all_unique_lib(response)
            all_avail_bks_by_lib = process.process_all_avail_bks_by_lib(
                response)
            lib_book_summary = process.process_lib_book_summary(
                all_unique_lib, all_avail_bks_by_lib)

            update_status = None
            if m_db.mg_query_status(db=db, username=username.get("UserName")):
                update_status = "Updating In Progress!"

            output = []
            for book in response:
                if library in book['BranchName'].lower():
                    output.append(book)

            lib_avail = len(process.process_all_avail_books(output))
            lib_all = len(process.process_all_unique_books(output))

            unique_lib = None
            if len(set([i['BranchName'] for i in response])) == 1:
                unique_lib = output[0]['BranchName']

            return templates.TemplateResponse("result.html", {
                "request": request,
                "username": username.get("UserName"),
                "api_data": output,
                'library': library,
                'all_unique_books': all_unique_books,
                'all_avail_books': all_avail_books,
                'all_unique_lib': all_unique_lib,
                'unique_lib': unique_lib,
                'avail_books': all_avail_bks_by_lib,
                'lib_book_summary': lib_book_summary,
                'lib_avail': lib_avail,
                'lib_all': lib_all,
                'status': update_status
            })

        else:
            return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")


def update_bk_avail_in_mongo(db, bid_no):
    """ This function does three things
    1. Make API calls to NLB to get book availability
    2. Process and combine the records into a single List[Dict]
    3. Delete existing book available records in MongoDB
    4. Ingest new book available records into MongoDB

    """
    try:
        # Make API call on book availability
        bk = nlb_rest_api.get_rest_nlb_api("GetAvailabilityInfo", input=bid_no)

        # Process and combine records
        all_books_avail = []
        for book in nlb_rest_api.process_rest_all_lib_avail(bk):
            books_avail = nlb_rest_api.process_single_bk_avail(book)
            books_avail.update({"BID": str(bid_no)})
            all_books_avail.append(books_avail)

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

    book_title_rest_api = nlb_rest_api.get_rest_nlb_api(
        "GetTitleDetails", input=bid_no)
    book_title = nlb_rest_api.process_rest_bk_info(book_title_rest_api)
    book_title.update({"BID": str(bid_no)})

    # Consider keeping this so that I can show this as well
    del book_title['PublishYear']

    m_db.mg_add_book_info(db=db, books_info_input=book_title)


@app.post("/update_book/{BID}", response_class=HTMLResponse)
async def update_book(BID: str,
                      db=Depends(get_db),
                      username=Depends(manager)):

    api_result = update_bk_avail_in_mongo(db, BID)

    if api_result.get("API call"):
        return RedirectResponse("/results", status_code=status.HTTP_302_FOUND)


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


@app.post("/update_user_books/{username}", response_class=HTMLResponse)
async def update_user_current_books(background_tasks: BackgroundTasks,
                                    db=Depends(get_db),
                                    username=Depends(manager)
                                    ):
    """ Updates availability of all user's saved books """
    background_tasks.add_task(update_all_user_books, db, username)
    return RedirectResponse("/results", status_code=status.HTTP_302_FOUND)


# Adds book into user account
@app.post("/ingest_book/{BID}", response_class=HTMLResponse)
async def api_book_ingest(BID: str,
                          db=Depends(get_db),
                          username=Depends(manager)):

    # Makes API to bk info and bk avail and ingest the data into DB
    m_db.mg_add_user_book(db=db,
                          username=username.get("UserName"),
                          bid_no=BID)

    bk_info_api_call_n_db_ingest(db=db, bid_no=BID)
    update_bk_avail_in_mongo(db, BID)

    return RedirectResponse(f"/{username.get('UserName')}/search",
                            status_code=status.HTTP_302_FOUND)


@app.post("/delete_book/{BID}", response_class=HTMLResponse)
async def delete_book(BID: str,
                      db=Depends(get_db),
                      username=Depends(manager)):

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

    return RedirectResponse(f"/{username.get('UserName')}/yourbooks",
                            status_code=status.HTTP_302_FOUND)


# To work on this!
@app.get("/{username}/search/", response_class=HTMLResponse)
async def show_search_books(request: Request,
                            book_search: Optional[str] = None,
                            db=Depends(get_db),
                            username=Depends(manager)):

    try:
        response = process_user_book_data(
            db=db, username=username.get("UserName"))

        update_status = None
        if m_db.mg_query_status(db=db, username=username.get("UserName")):
            update_status = "Updating In Progress!"

        # Processing necessary statistics
        all_unique_books = process.process_all_unique_books(response)
        all_avail_books = process.process_all_avail_books(response)
        all_unique_lib = process.process_all_unique_lib(response)
        all_avail_bks_by_lib = process.process_all_avail_bks_by_lib(response)
        lib_book_summary = process.process_lib_book_summary(
            all_unique_lib, all_avail_bks_by_lib)

        text_output = "Please search for your book title"
        final_response = list()

        if book_search:
            book_search = re.sub('\W+', ' ', book_search)
            print(f"{book_search} is happening")

            if book_search.isdigit() and len(book_search) in [10, 13]:
                print("ISBN")
                book_search = str(book_search)
                books = nlb_rest_api.get_rest_nlb_api(
                    "SearchTitles", book_search, "ISBN")

            else:
                print("title")
                books = nlb_rest_api.get_rest_nlb_api(
                    "SearchTitles", book_search)

            elist = [400, 404, 500, 401, 405, 429]

            if books.get("totalRecords") == 0:
                text_output = f"There are no records with '{book_search}'"

            elif books.get("statusCode") in elist:
                text_output = f"There are no records with '{book_search}'"

            else:
                # Get main list of books
                searched_books = []
                searched_books.append(books.get("titles"))

                # Check for pagination
                has_more_records = books.get("hasMoreRecords")
                counter = 0
                while has_more_records:
                    counter += 1
                    set_id = books.get("setId")
                    last_irn = books.get("lastIrn")
                    books = nlb_rest_api.get_rest_nlb_api(
                        "SearchTitles",
                        input=book_search,
                        search_on='Title',
                        setid=set_id,
                        lastirn=last_irn)

                    searched_books.append(books.get('titles'))
                    has_more_records = books.get("hasMoreRecords")

                if counter > 0:
                    p_searched_books = [i for sl in searched_books for i in sl]
                else:
                    p_searched_books = searched_books[0]

                output_list = []
                for book in p_searched_books:
                    get_isbn = book.get("isbns")
                    if get_isbn:
                        if "electronic" not in get_isbn:
                            output_list.append(book)
                    else:
                        output_list.append(book)

                final_output = [nlb_rest_api.process_rest_bk_info(
                    i) for i in output_list]

                # Search user book BIDs and
                # disable add books for books already saved by user
                user_books = m_db.mg_query_user_bookmarked_books(
                    db=db, username=username.get("UserName"))

                user_books_bids = [i.get("BID") for i in user_books]

                for i in final_output:
                    try:
                        i['TitleName'] = i['TitleName'].split(
                            "/")[0].strip() + " | " + str(i['BID'])

                        i['PublishYear'] = "Y" + i['PublishYear']

                        disable = "disabled" if str(
                            i['BID']) in user_books_bids else ""

                        i['BID'] = disable + " | " + str(i["BID"])

                        final_response.append(i)
                    except Exception:
                        pass

        return templates.TemplateResponse("search.html", {
            "request": request,
            "keyword": book_search,
            "username": username.get("UserName"),
            "api_data": final_response,
            "text_output": text_output,
            'all_unique_books': all_unique_books,
            'all_avail_books': all_avail_books,
            'all_unique_lib': all_unique_lib,
            'avail_books': all_avail_bks_by_lib,
            'lib_book_summary': lib_book_summary,
            "status": update_status
        })

    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")
