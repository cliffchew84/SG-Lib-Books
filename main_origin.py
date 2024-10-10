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
import supabase
import time
import os
import re

# My own packages
import process as p
import nlb_api as n_api
import supa_db as s_db
import m_db

# Load environment variables
SECRET_KEY = os.environ["mongo_secret_key"]
ACCESS_TOKEN_EXPIRY = 240

# APPLICATION_ID = os.environ['nlb_rest_app_id']
# API_KEY = os.environ['nlb_rest_api_key']

manager = LoginManager(SECRET_KEY, token_url="/login", use_cookie=True)
manager.cookie_name = "auth"


def get_db():
    return s_db.connect_sdb()


# Password hashing setup
pwd_ctx = CryptContext(schemes=['bcrypt'], deprecated="auto")


def get_hashed_password(plain_password):
    return pwd_ctx.hash(plain_password)


def verify_password(plain_password, hashed_password):
    return pwd_ctx.verify(plain_password, hashed_password)


@manager.user_loader()
def get_user(username: str):
    db = s_db.connect_sdb()
    user = s_db.q_username(db=db, username=username)
    if user:
        return user


def auth_user(username: str,
              password: str,
              db=Depends(get_db)):
    user = s_db.q_username(db=db, username=username)
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
    db = s_db.connect_sdb()
    user = s_db.q_username(db=db, username=username)
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
        if s_db.q_username(db=db, username=username):
            invalid = True

        if not invalid:
            s_db.add_user(db=db, username=username, hashed_pw=hashed_password)
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRY)
            access_token = manager.create_access_token(
                data={"sub": username},
                expires=access_token_expires)

            resp = RedirectResponse("/register_complete/" +
                                    urllib.parse.quote(username),
                                    status_code=status.HTTP_302_FOUND)
            # [TODO]
            s_db.event_tracking(db, 'users', username, "registered_time")
            s_db.event_tracking(db, 'users', username, 'latest_login')
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
    user = auth_user(username=form_data.username,
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
    s_db.event_tracking(db, 'users', user.get("UserName"), 'latest_login')
    return resp


@app.get("/forgot_password", response_class=HTMLResponse)
async def forgot_password(request: Request, wrong_question=False):
    return templates.TemplateResponse("forgot_password.html", {
        "request": request})


@app.get("/reset_password/", response_class=HTMLResponse)
async def reset_password(request: Request,
                         username: str = Form(...),
                         pw_qn: str = Form(...),
                         pw_ans: str = Form(...),
                         new_password: str = Form(...)):
    db = s_db.connect_sdb()
    user = s_db.q_user(db=db, username=username)
    if user:
        if user.get("pw_qn") == pw_qn & user.get("pw_ans") == pw_ans:
            hashed_password = get_hashed_password(new_password)
            new_dict = {"HashedPassword": hashed_password}
            s_db.update_user_info(db, username.get("UserName"), new_dict)
    else:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User email not found")
    return RedirectResponse("/", status_code=status.HTTP_302_FOUND)


@app.get("/{username}/main")
async def htmx_main(request: Request,
                    db=Depends(get_db),
                    username=Depends(manager)):

    username=username.get("UserName")
    query = s_db.q_user_bks(username)
    response = p.process_user_bks(query)

    # Processing necessary statistics
    all_unique_books = p.get_unique_bks(response)
    all_avail_books = p.get_avail_bks(response)
    unique_libs = p.get_unique_libs(response)
    avail_bks_by_lib = p.get_avail_bks_by_lib(response)
    lib_book_summary = p.get_lib_bk_summary(unique_libs, avail_bks_by_lib)

    update_status = None
    if s_db.q_status(db=db, username=username):
        update_status = "Updating In Progress!"

    # Check if user has a default library
    user_info = s_db.q_user_info(db, username)
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

    lib_avail = len(p.get_avail_bks(output))
    lib_all = len(p.get_unique_bks(output))

    return templates.TemplateResponse("main.html", {
        "request": request,
        "username": username,
        "api_data": output,
        'all_avail_books': all_avail_books,
        'all_unique_books': all_unique_books,
        'avail_books': avail_bks_by_lib,
        'lib_book_summary': lib_book_summary,
        'lib_avail': lib_avail,
        'lib_all': lib_all,
        "library": preferred_lib,
        "status": update_status
    })

@app.get("/{username}/user_bks")
async def current_bks(request: Request,
                      db=Depends(get_db),
                      username=Depends(manager)):
    """ Used by htmx to render user books within main_content <div> """
    username=username.get("UserName")
    update_status = None
    if s_db.q_status(db=db, username=username):
        update_status = "Updating In Progress... Please refresh to update!"

    output = []
    if username:
        output = s_db.q_user_bks_subset(username=username)
        return templates.TemplateResponse("user_bks.html", {
            "request": request,
            "username": username,
            "api_data": output,
            "status": update_status
        })
    else:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)


@app.get("/{username}/lib/{library}/", response_class=HTMLResponse)
async def show_avail_m_books(request: Request,
                             library: Optional[str],
                             db=Depends(get_db),
                             username=Depends(manager)):
    try:
        if username:
            username=username.get("UserName")
            update_status = None
            if s_db.q_status(db=db, username=username):
                update_status = "Updating In Progress!"

            # Query entire user books - Inefficient
            query = s_db.q_user_bks(username=username)
            response = p.process_user_bks(query)
            all_unique_books = p.get_unique_bks(response)
            all_avail_books = p.get_avail_bks(response)

            if library != 'all':
                output = []
                for book in response:
                    if library in book['BranchName'].lower():
                        output.append(book)
            else:
                output = response

            lib_avail = len(p.get_avail_bks(output))
            lib_all = len(p.get_unique_bks(output))

            return templates.TemplateResponse("result.html", {
                "request": request,
                "username": username,
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


def update_bk_avail_supa(db, bid_no: str):
    """ 
    Takes in single BID to get its avail info
    Processes data for Supabase

    # Should separate these functions!
    Delete existing Supabase data if found
    Inject new data into Supabase 
    """
    try:
        # Make API call on book availability
        bk = n_api.get_bk_data(
            "GetAvailabilityInfo", input_dict={"BRN": bid_no})
        all_avail_bks = [p.process_bk_avail(i) for i in bk.get("items")]

        if len(all_avail_bks) > 0:
            s_db.delete_bk_avail(db=db, bid_no=bid_no)
            s_db.add_avail_bks(db=db, books_avail=all_avail_bks)

            return {"API call": True}
        else:
            # Something wrong with the NLB API and nothing is updated...
            return {"API call": False}

    except Exception:
        return {"API call": False}




@app.post("/update_book/{BID}", response_class=HTMLResponse)
async def update_book(BID: str,
                      db=Depends(get_db),
                      username=Depends(manager)):

    api_result = update_bk_avail_supa(db, BID)
    if api_result.get("API call"):
        return RedirectResponse(f"/{username.get('UserName')}/main",
                                status_code=status.HTTP_302_FOUND)


def update_all_user_books(db, username):
    """ Update all books linked to user."""
    username = username.get("UserName")

    user_bids = s_db.q_user_bks_bids(db=db, username=username)
    s_db.insert_status(db, username=username)
    s_db.update_user_info(db, username, {'books_updated': 0})
    for i, ubid in enumerate(user_bids):
        bid_no = ubid.get("BID")
        print(bid_no)

        time.sleep(2)
        update_bk_avail_supa(db, bid_no)

        s_db.update_user_info(db, username, {'books_updated': i+1})
    s_db.delete_status(db, username=username)
    return {"message": "All user books updated!"}


@app.post("/m_update_user_books/{username}", response_class=HTMLResponse)
async def update_user_saved_bks(background_tasks: BackgroundTasks,
                                db=Depends(get_db),
                                username=Depends(manager)):
    """ Updates availability of all user's saved books """
    background_tasks.add_task(update_all_user_books, db, username)
    return RedirectResponse(f"/{username.get('UserName')}/lib/all",
                            status_code=status.HTTP_302_FOUND)


@app.get("/book_status/{book_saved}")
async def book_status_progress_bar(request: Request,
                                   book_saved: int,
                                   db=Depends(get_db),
                                   username=Depends(manager)):

    username = username.get("UserName")
    books_updated = s_db.q_user_info(
        db=db, username=username).get("books_updated")

    progress = 0
    if books_updated > 0:
        progress = (books_updated / book_saved) * 100

    update_status = None
    if s_db.q_status(db=db, username=username):
        update_status = "Updating! Please Refresh when Done"
    return templates.TemplateResponse("book_updates.html", {
        "request": request,
        "progress": progress,
        "status": update_status
    })


@app.get("/update_header", response_class=HTMLResponse)
async def update_header(request: Request,
                        db=Depends(get_db),
                        username=Depends(manager)):

    username = username.get("UserName")
    query = s_db.q_user_bks(username=username)
    response = p.process_user_bks(query)

    # Processing necessary statistics
    all_unique_books = p.get_unique_bks(response)
    all_avail_books = p.get_avail_bks(response)
    unique_libs = p.get_unique_libs(response)
    avail_bks_by_lib = p.get_avail_bks_by_lib(response)
    lib_book_summary = p.get_lib_bk_summary(unique_libs, avail_bks_by_lib)

    update_status = None
    if s_db.q_status(db=db, username=username):
        update_status = "Updating In Progress!"

    # Check if user has a default library
    user_info = s_db.q_user_info(db, username)
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

    lib_avail = len(p.get_avail_bks(output))
    lib_all = len(p.get_unique_bks(output))

    return templates.TemplateResponse("navbar.html", {
        "request": request,
        "username": username,
        "api_data": output,
        'all_avail_books': all_avail_books,
        'all_unique_books': all_unique_books,
        'avail_books': avail_bks_by_lib,
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
    username = username.get("UserName")
    for bid in bids:
        print(bid)
        # Makes API to bk info and bk avail and ingest the data into DB
        bk_title = n_api.get_process_bk_info(bid_no=bid)

        time.sleep(2)
        update_bk_avail_supa(db, bid)

        # Do all the adding at the end, after everything is confirmed
        # This also doesn't require any time.sleep() as this is with my own DB
        s_db.add_user_book(db=db, username=username, bid_no=bid)
        s_db.add_book_info(db=db, books_info=bk_title)

        print("print started book_available update")

    # Update the books calculation on the navbar
    query = s_db.q_user_bks(username=username)
    response = p.process_user_bks(query)

    # Processing necessary statistics
    all_unique_books = p.get_unique_bks(response)
    all_avail_books = p.get_avail_bks(response)
    unique_libs = p.get_unique_libs(response)
    avail_bks_by_lib = p.get_avail_bks_by_lib(response)
    lib_book_summary = p.get_lib_bk_summary(unique_libs, avail_bks_by_lib)

    return templates.TemplateResponse("navbar.html", {
        "request": request,
        "username": username,
        'all_avail_books': all_avail_books,
        'all_unique_books': all_unique_books,
        'lib_book_summary': lib_book_summary,
    })


@app.delete("/delete_bk/{bid}", response_class=HTMLResponse)
async def delete_bk(request: Request,
                    bid: int,
                    db=Depends(get_db),
                    username=Depends(manager)):
    username=username.get("UserName") 
    final_count = s_db.q_bid_counter(bid_no=str(bid)) 

    # If book is only linked to one user,
    # delete book available and info records
    if final_count == 1:
        s_db.delete_bk_avail(db=db, bid_no=bid)
        s_db.delete_bk_info(db=db, bid_no=bid)
    s_db.delete_user_bk(db=db, username=username, bid_no=bid)

    return ""


@app.post("/delete_books", response_class=HTMLResponse)
async def delete_books(request: Request,
                       bids: list = Form(...),
                       db=Depends(get_db),
                       username=Depends(manager)):
    username=username.get("UserName")
    for bid in bids:
        final_count = s_db.q_bid_counter(bid_no=str(bid)) 
        # If book is only linked to one user,
        # delete book available and info records
        if final_count == 1:
            s_db.delete_bk_avail(db=db, bid_no=bid)
            s_db.delete_bk_info(db=db, bid_no=bid)
        s_db.delete_user_bk(db=db, username=username, bid_no=bid)

    output = []
    if username:
        output = s_db.q_user_bks_subset(username=username)
        query = s_db.q_user_bks(username=username)
        response = p.process_user_bks(query)

        # Processing necessary statistics
        all_unique_books = p.get_unique_bks(response)
        all_avail_books = p.get_avail_bks(response)
        unique_libs = p.get_unique_libs(response)
        avail_bks_by_lib = p.get_avail_bks_by_lib(response)
        lib_book_summary = p.get_lib_bk_summary(unique_libs, avail_bks_by_lib)

    return templates.TemplateResponse("user_bks.html", {
        "request": request,
        "username": username,
        "api_data": output,
        'all_avail_books': all_avail_books,
        'all_unique_books': all_unique_books,
        'lib_book_summary': lib_book_summary,
    })


@app.get("/htmx_search", response_class=HTMLResponse)
async def htmx_bk_search(request: Request,
                         e_resources: Optional[str] = None,
                         book_search: Optional[str] = None,
                         author: Optional[str] = None,
                         db=Depends(get_db),
                         username=Depends(manager)):
    """ Calls NLB API GetTitles Search and show results in search_table.html"""
    bk_output, search_input = [], dict()
    username = username.get("UserName")

    if book_search:
        c_book_search = re.sub(r'[^a-zA-Z0-9\s]', ' ', book_search)
        search_input.update({"Title": c_book_search})

    if author:
        c_author = re.sub(r'[^a-zA-Z0-9\s]', ' ', author)
        search_input.update({"Author": c_author})

    if book_search or author:
        titles = n_api.get_bk_data(ext_url="GetTitles",
                                   input_dict=search_input,
                                   offset=0)
        total_records = titles.get("totalRecords", None)
        more_records = titles.get("hasMoreRecords", None)
        pag_links = p.pg_links(0, total_records)
        search_params = {"Title": book_search, 'Author' : author}
        s_db.user_search_tracking(
            db, table_name="user_search", 
            username=username, 
            search_params=search_params)

        errors = [400, 404, 500, 401, 405, 429]
        if titles.get("statusCode") in errors or titles.get("totalRecords") == 0:
            # Return temply table
            return templates.TemplateResponse("partials/search_table.html", {
            "request": request,
            "keyword": book_search,
            "author": author,
            "username": username,
            "api_data": bk_output,
        })

        else:
            all_titles = p.process_title(titles)
            # Only keep physical books for now
            final_titles = [t for t in all_titles if t['type'] == "Book"]
            if e_resources:
                print("Including ebooks")
                ebooks = [t for t in all_titles if t['type'] == "Ebook"]
                final_titles += ebooks

            # Search user book BIDs and disable add book if user saved the book
            user_books = s_db.q_user_bks(username=username)
            bid_checks = set(i.get("BID") for i in user_books)
            for bk in final_titles:
                bid = bk.get('BID') if bk.get(
                    'DigitalID') is None else bk.get('DigitalID')
                bid = str(bid)

                title = bk.get("TitleName", " / ").split(" / ", 1)[0].strip()

                # Enable disable button if book is already saved
                disable = "disabled" if bid in bid_checks else ""

                bk['TitleName'] = title + " | " + bid
                bk['BID'] = disable + " | " + bid

                bk_output.append(bk)

    return templates.TemplateResponse("partials/search_table.html", {
        "request": request,
        "keyword": book_search,
        "author": author,
        "username": username,
        "api_data": bk_output,
        "total_records": total_records,
        "more_records": more_records,
        "pag_links": pag_links,
        "e_resources": e_resources
    })


@app.get("/navigate_search", response_class=HTMLResponse)
async def htmx_paginate_bk_search(request: Request,
                                  book_search: Optional[str] = None,
                                  author: Optional[str] = None,
                                  offset: Optional[str] = None,
                                  e_resources: Optional[str] = None,
                                  db=Depends(get_db),
                                  username=Depends(manager)):
    """ Calls new GetTitles Search and show results in search_table.html"""
    final_response, search_input = list(), dict()
    username=username.get("UserName")

    if book_search:
        c_book_search = re.sub(r'[^a-zA-Z0-9\s]', ' ', book_search)
        search_input.update({"Title": c_book_search})

    if author:
        c_author = re.sub(r'[^a-zA-Z0-9\s]', ' ', author)
        search_input.update({"Author": c_author})

    if book_search or author:
        titles = n_api.get_bk_data(ext_url="GetTitles", 
                                   input_dict=search_input, 
                                   offset=offset)
        total_records = titles.get("totalRecords")
        pag_links = p.pg_links(int(offset), total_records)

        errors = [400, 404, 500, 401, 405, 429]
        if titles.get("statusCode") in errors or titles.get("totalRecords") == 0:
            # return empty table
            return templates.TemplateResponse("partials/search_table.html", {
            "request": request,
            "keyword": book_search,
            "author": author,
            "username": username,
            "api_data": final_response,
        })

        else:
            all_titles = p.process_title(titles)
            more_records = titles.get("hasMoreRecords")

            # Only keep physical books for now
            final_titles = [t for t in all_titles if t['type'] == "Book"]

            if e_resources:
                print("Including ebooks")
                ebooks = [t for t in all_titles if t['type'] == "Ebook"]
                final_titles += ebooks

            # Search user book BIDs and disable add book if user saved the book
            user_books = s_db.q_user_bks(username=username)
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

    return templates.TemplateResponse("partials/search_table.html", {
        "request": request,
        "keyword": book_search,
        "author": author,
        "username": username,
        "api_data": final_response,
        "total_records": total_records,
        "more_records": more_records,
        "pag_links": pag_links,
        "e_resources": e_resources
    })


@app.get("/{username}/search/", response_class=HTMLResponse)
async def search_books(request: Request,
                         book_search: Optional[str] = None,
                         author: Optional[str] = None,
                         db=Depends(get_db),
                         username=Depends(manager)):
    update_status = None
    if s_db.q_status(db=db, username=username.get("UserName")):
        update_status = "Updating In Progress!"

    return templates.TemplateResponse("search.html", {
        "request": request,
        "keyword": book_search,
        "author": author,
        "username": username.get("UserName"),
        "status": update_status
    })


@app.get("/{username}/profile", response_class=HTMLResponse)
async def user_profile(request: Request,
                         db=Depends(get_db),
                         username=Depends(manager)):

    username=username.get("UserName")
    query = s_db.q_user_bks(username=username)
    response = p.process_user_bks(query)
    unique_libs = p.get_unique_libs(response)
    update_status = None
    if s_db.q_status(db=db, username=username):
        update_status = "Updating In Progress!"

    # Query user profile info from database
    user_info = s_db.q_user_info(db, username)
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "username": username,
        "email_address": user_info.get("email_address", None),
        "preferred_lib": user_info.get("preferred_lib", None),
        "pw_qn": user_info.get("pw_qn", None),
        "pw_ans": user_info.get("pw_ans", None),
        'all_unique_lib': unique_libs,
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

    username=username.get("UserName")
    # Update info
    new_dict = {'email_address': email_address,
                "preferred_lib": preferred_lib,
                "pw_qn": pw_qn,
                "pw_ans": pw_ans}
    if password:
        hashed_password = get_hashed_password(password)
        new_dict.update({"HashedPassword": hashed_password})

    s_db.update_user_info(db, username, new_dict)
    return RedirectResponse(f"/profile/{username}",
                            status_code=status.HTTP_302_FOUND)


@app.post("/delete_user/{username}", response_class=HTMLResponse)
async def delete_user(request: Request,
                      db=Depends(get_db),
                      username=Depends(manager)):
    s_db.delete_user(db, username=username.get("UserName"))
    return RedirectResponse("/logout", status_code=status.HTTP_302_FOUND)
