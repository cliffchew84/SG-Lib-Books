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
import time
import os
import re

# My own packages
import process
import nlb_rest_api
import m_db

# Test upload comment

# Load environment variables
SECRET_KEY = os.environ["mongo_secret_key"]
ACCESS_TOKEN_EXPIRY = 240

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
            output = m_db.get_user_saved_books(
                db=db, username=username.get("UserName"))

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
        bid = a.get("BID")
        title = a.get("TitleName").split("/", 1)[0]

        due_date = None
        if a.get("DueDate"):
            tmp_date = a.get("DueDate").split("T", 1)[0]
            input_date = datetime.strptime(tmp_date, "%Y-%m-%d")
            due_date = input_date.strftime("%d/%m")

        update_time = datetime.fromtimestamp(
            a.get("InsertTime"), pendulum.timezone("Asia/Singapore")
        ).strftime("%d/%m %H:%M")

        raw_status = a.get("StatusDesc")
        status = re.findall('Not Loan|Loan|Reference|Transit|$', raw_status)[0]
        status = "Available" if status == "Not Loan" else status
        status = raw_status if status == "" else status

        if due_date is not None:
            status = status + '[' + str(due_date) + ']'

        branch_name = a.get("BranchName")
        if "Lifelong Learning" in branch_name:
            library = "Lifelong Learning Institute"
        elif "Public Library" in branch_name:
            library = branch_name.split("Public Library", 1)[0]
        elif "Library" in branch_name:
            library = branch_name.split("Library", 1)[0]
        else:
            library = branch_name

        response.append({
            "TitleName": title,
            "BranchName": library,
            "CallNumber": a.get("CallNumber").split(" -", 1)[0],
            "StatusDesc": status,
            "UpdateTime": update_time,
            "BID": bid})

    return response


@app.get("/{username}/m_lib/{library}/", response_class=HTMLResponse)
async def show_avail_m_books(request: Request,
                             library: Optional[str],
                             db=Depends(get_db),
                             username=Depends(manager)):
    try:
        if username:
            update_status = None
            if m_db.mg_query_status(db=db, username=username.get("UserName")):
                update_status = "Updating In Progress!"

            # Query entire user books - Inefficient
            response = process_user_book_data(
                db=db, username=username.get("UserName"))

            all_unique_books = process.process_all_unique_books(response)
            all_avail_books = process.process_all_avail_books(response)

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
    try:
        book_title['TitleName'] = book_title['TitleName'].split("/", 1)[0]
    except Exception:
        pass

    print(book_title)
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
    """ Update all books linked to user."""

    user_bids = m_db.mg_query_user_books_w_bid(
        db=db, username=username.get("UserName"))

    m_db.mg_insert_status(db, username=username.get("UserName"))

    m_db.mg_update_user_info(db,
                             username=username.get("UserName"),
                             dict_values_to_add={'books_updated': 0})

    for i, ubid in enumerate(user_bids):
        bid_no = ubid.get("BID")
        print(bid_no)
        time.sleep(1)
        update_bk_avail_in_mongo(db, bid_no)
        m_db.mg_update_user_info(db,
                                 username=username.get("UserName"),
                                 dict_values_to_add={'books_updated': i+1})

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


@app.get("/book_status/{book_saved}")
async def book_status_progress_bar(request: Request,
                                   book_saved: int,
                                   db=Depends(get_db),
                                   username=Depends(manager)):

    books_updated = m_db.mg_query_user_info(
        db=db, username=username.get("UserName")).get("books_updated")

    progress = 0
    if books_updated > 0:
        progress = (books_updated / book_saved) * 100

    update_status = None
    if m_db.mg_query_status(db=db, username=username.get("UserName")):
        update_status = "Updating! Please Refresh when Done"

    print(update_status)

    return templates.TemplateResponse("book_updates.html", {
        "request": request,
        "progress": progress,
        "status": update_status
    })


@app.get("/update_header", response_class=HTMLResponse)
async def update_header(request: Request,
                        db=Depends(get_db),
                        username=Depends(manager)):

    response = process_user_book_data(
        db=db, username=username.get("UserName"))

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

    return templates.TemplateResponse("m_navbar.html", {
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


# Experimental navbar updates
@app.post("/ingest_books_navbar", response_class=HTMLResponse)
async def ingest_books_navbar(request: Request,
                              bids: list = Form(...),
                              db=Depends(get_db),
                              username=Depends(manager)):

    for bid in bids:
        BID = str(bid)
        print(BID)
        # Makes API to bk info and bk avail and ingest the data into DB
        m_db.mg_add_user_book(db=db,
                              username=username.get("UserName"),
                              bid_no=BID)

        bk_info_api_call_n_db_ingest(db=db, bid_no=BID)
        time.sleep(2)
        update_bk_avail_in_mongo(db, BID)
        print("print started book_available update")

    # Update the books calculation on the navbar
    response = process_user_book_data(
        db=db, username=username.get("UserName"))

    # Processing necessary statistics
    all_unique_books = process.process_all_unique_books(response)
    all_avail_books = process.process_all_avail_books(response)
    all_unique_lib = process.process_all_unique_lib(response)
    all_avail_bks_by_lib = process.process_all_avail_bks_by_lib(response)
    lib_book_summary = process.process_lib_book_summary(
        all_unique_lib, all_avail_bks_by_lib)

    return templates.TemplateResponse("m_navbar.html", {
        "request": request,
        "username": username.get("UserName"),
        'all_avail_books': all_avail_books,
        'all_unique_books': all_unique_books,
        'lib_book_summary': lib_book_summary,
    })


@app.post("/delete_books", response_class=HTMLResponse)
async def delete_books(request: Request,
                       bids: list = Form(...),
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

    output = []
    if username:
        # Get all the books linked to the user.
        # This is the complicated query
        output = m_db.get_user_saved_books(
            db=db, username=username.get("UserName"))

        # Update books available calculation in navbar
        response = process_user_book_data(
            db=db, username=username.get("UserName"))

        # Processing necessary statistics
        all_unique_books = process.process_all_unique_books(response)
        all_avail_books = process.process_all_avail_books(response)
        all_unique_lib = process.process_all_unique_lib(response)
        all_avail_bks_by_lib = process.process_all_avail_bks_by_lib(response)
        lib_book_summary = process.process_lib_book_summary(
            all_unique_lib, all_avail_bks_by_lib)

    return templates.TemplateResponse("m_yourbooks.html", {
        "request": request,
        "username": username.get("UserName"),
        "api_data": output,
        'all_avail_books': all_avail_books,
        'all_unique_books': all_unique_books,
        'lib_book_summary': lib_book_summary,
    })


def pg_links(offset, total):
    """ Create pagination for NLB Search function """
    items = 30
    previous = offset - items if offset != 0 else None
    current = offset
    next = offset + items if (offset + items < total) else None
    last = items * (total // items) if next is not None else None

    return {"previous": previous,
            "current": current,
            "next": next,
            "last": last}


@app.get("/htmx_search", response_class=HTMLResponse)
async def htmx_search_books(request: Request,
                            e_resources: Optional[str] = None,
                            book_search: Optional[str] = None,
                            author: Optional[str] = None,
                            db=Depends(get_db),
                            username=Depends(manager)):

    """ Calls NLB API GetTitles Search and show results in search_table.html"""
    final_response = list()
    search_input = dict()

    if book_search:
        c_book_search = re.sub(r'[^a-zA-Z0-9\s]', ' ', book_search)
        search_input.update({"Title": c_book_search})

    if author:
        c_author = re.sub(r'[^a-zA-Z0-9\s]', ' ', author)
        search_input.update({"Author": c_author})

    if book_search or author:
        titles = nlb_rest_api.get_rest_title(
            input_dict=search_input, offset=0)
        total_records = titles.get("totalRecords")
        more_records = titles.get("hasMoreRecords")

        offset_links = pg_links(0, total_records)

        search_params = dict()
        search_params['title'] = book_search
        search_params['author'] = author

        m_db.mg_user_search_tracking(db,
                                     table="user_search",
                                     username=username.get("UserName"),
                                     search_params=search_params)

        empty_table_result = templates.TemplateResponse("search_table.html", {
            "request": request,
            "keyword": book_search,
            "author": author,
            "username": username.get("UserName"),
            "api_data": final_response,
        })

        elist = [400, 404, 500, 401, 405, 429]

        if titles.get("statusCode") in elist:
            return empty_table_result

        elif titles.get("totalRecords") == 0:
            return empty_table_result

        else:
            all_titles = nlb_rest_api.get_title_process(titles)

            # Only keep physical books for now
            books = [t for t in all_titles if t['type'] == "Book"]

            if e_resources:
                print("I am including ebooks")
                ebooks = [t for t in all_titles if t['type'] == "Ebook"]

                final_titles = books + ebooks

            else:
                final_titles = books

            # Search user book BIDs and disable add book if user saved the book
            user_books = m_db.mg_query_user_bookmarked_books(
                db=db, username=username.get("UserName"))

            bid_checks = set(i.get("BID") for i in user_books)

            for book in final_titles:
                bid = book.get('BID') if book.get(
                    'DigitalID') is None else book.get('DigitalID')
                bid = str(bid)

                title = book.get("TitleName", "")
                title = title.split(" / ", 1)[0].strip()

                # Enable disable button if book is already saved
                disable = "disabled" if bid in bid_checks else ""

                book['TitleName'] = title + " | " + bid
                book['BID'] = disable + " | " + bid

                final_response.append(book)

    return templates.TemplateResponse("search_table.html", {
        "request": request,
        "keyword": book_search,
        "author": author,
        "username": username.get("UserName"),
        "api_data": final_response,
        "total_records": total_records,
        "more_records": more_records,
        "offset_links": offset_links,
        "e_resources": e_resources
    })


@app.get("/navigate_search", response_class=HTMLResponse)
async def htmx_paginate_search_books(request: Request,
                                     book_search: Optional[str] = None,
                                     author: Optional[str] = None,
                                     offset: Optional[str] = None,
                                     e_resources: Optional[str] = None,
                                     db=Depends(get_db),
                                     username=Depends(manager)):

    """ Calls new GetTitles Search and show results in search_table.html"""

    final_response = list()
    search_input = dict()

    if book_search:
        c_book_search = re.sub(r'[^a-zA-Z0-9\s]', ' ', book_search)
        search_input.update({"Title": c_book_search})

    if author:
        c_author = re.sub(r'[^a-zA-Z0-9\s]', ' ', author)
        search_input.update({"Author": c_author})

    if book_search or author:
        titles = nlb_rest_api.get_rest_title(input_dict=search_input,
                                             offset=offset)
        total_records = titles.get("totalRecords")

        offset_links = pg_links(int(offset), total_records)
        print(offset_links)

        empty_table_result = templates.TemplateResponse("search_table.html", {
            "request": request,
            "keyword": book_search,
            "author": author,
            "username": username.get("UserName"),
            "api_data": final_response,
        })

        elist = [400, 404, 500, 401, 405, 429]

        if titles.get("statusCode") in elist:
            return empty_table_result

        elif titles.get("totalRecords") == 0:
            return empty_table_result

        else:
            all_titles = nlb_rest_api.get_title_process(titles)
            more_records = titles.get("hasMoreRecords")

            # Only keep physical books for now
            books = [t for t in all_titles if t['type'] == "Book"]

            if e_resources:
                print("I am including ebooks")
                ebooks = [t for t in all_titles if t['type'] == "Ebook"]

                final_titles = books + ebooks

            else:
                final_titles = books

            # Search user book BIDs and disable add book if user saved the book
            user_books = m_db.mg_query_user_bookmarked_books(
                db=db, username=username.get("UserName"))

            bid_checks = set(i.get("BID") for i in user_books)

            for book in final_titles:
                # Prep for eResources in the future
                bid = book.get('BID') if book.get(
                    'DigitalID') is None else book.get('DigitalID')
                bid = str(bid)

                title = book.get("TitleName", "")
                title = title.split(" / ", 1)[0].strip()

                # Enable disable button if book is already saved
                disable = "disabled" if bid in bid_checks else ""

                book['TitleName'] = title + " | " + bid
                book['BID'] = disable + " | " + bid

                final_response.append(book)

    return templates.TemplateResponse("search_table.html", {
        "request": request,
        "keyword": book_search,
        "author": author,
        "username": username.get("UserName"),
        "api_data": final_response,
        "total_records": total_records,
        "more_records": more_records,
        "offset_links": offset_links,
        "e_resources": e_resources
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

    final_output = m_db.get_lib_events(db, lib)

    return templates.TemplateResponse("m_lib_events.html", {
        "request": request,
        "username": username.get("UserName"),
        "lib_events": final_output,
        "total_records": len(final_output),
        'lib_locations': lib_locations,
        "selected_lib": lib
    })
