import time
from typing import Optional

from fastapi import (
    FastAPI,
    status,
    Request,
    Form,
    Depends,
    BackgroundTasks,
    Cookie,
)
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


from src import m_db
from src import supa_db as s_db
from src import nlb_api as n_api
from src import process as p
from src.api import api
from src.config import settings
from src.utils import templates, username_email_resol


# Think about adding back mongoDB stuff
# user_status

# Environment setup
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Application code
app = FastAPI(
    title=settings.APP_NAME, version=settings.VERSION, description=settings.DESCRIPTION
)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(api)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    return s_db.connect_sdb()


def username_email_resol(user_info: str):
    """In the current new flow, username == email
    To cover legacy situation where username != email
    """
    email, username = user_info.split(" | ")
    if not username:
        username = email
    return username


@app.get("/main", response_class=HTMLResponse)
async def main(request: Request, user_info: str = Cookie(None), db=Depends(get_db)):
    if user_info:
        username = username_email_resol(user_info)

        # Continue to extract user book info
        query = s_db.q_user_bks(username)
        response = p.process_user_bks(query)

        # Processing necessary statistics
        all_unique_books = p.get_unique_bks(response)
        all_avail_books = p.get_avail_bks(response)
        unique_libs = p.get_unique_libs(response)
        avail_bks_by_lib = p.get_avail_bks_by_lib(response)
        lib_book_summary = p.get_lib_bk_summary(unique_libs, avail_bks_by_lib)

        mdb = m_db.connect_mdb()
        mdb = mdb["nlb"]
        update_status = None
        if m_db.q_status(db=mdb, username=username):
            update_status = " "

        # Check if user has a default library
        user_info = s_db.q_user_info(db, username)
        preferred_lib = user_info.get("preferred_lib")

        if preferred_lib:
            preferred_lib = preferred_lib.lower()
            output = []
            for book in response:
                if preferred_lib in book["BranchName"].lower():
                    output.append(book)
        else:
            preferred_lib = "all"
            output = response

        lib_avail = len(p.get_avail_bks(output))
        lib_all = len(p.get_unique_bks(output))

        return templates.TemplateResponse(
            "main.html",
            {
                "request": request,
                "username": username,
                "api_data": output,
                "all_avail_books": all_avail_books,
                "all_unique_books": all_unique_books,
                "avail_books": avail_bks_by_lib,
                "lib_book_summary": lib_book_summary,
                "lib_avail": lib_avail,
                "lib_all": lib_all,
                "library": preferred_lib,
                "status": update_status,
            },
        )

    else:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)


@app.get("/user_bks")
async def current_bks(
    request: Request, db=Depends(get_db), user_info: str = Cookie(None)
):
    """Used by htmx to render user books within main_content <div>"""

    username = username_email_resol(user_info)
    mdb = m_db.connect_mdb()
    mdb = mdb["nlb"]
    update_status = None
    if m_db.q_status(db=mdb, username=username):
        update_status = " "

    output = []
    if username:
        output = s_db.q_user_bks_subset(username=username)
        return templates.TemplateResponse(
            "user_bks.html",
            {
                "request": request,
                "username": username,
                "api_data": output,
                "status": update_status,
            },
        )
    else:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)


# Start my edits from here
@app.get("/lib/{library}/", response_class=HTMLResponse)
async def show_avail_bks(
    request: Request,
    library: Optional[str],
    db=Depends(get_db),
    user_info: str = Cookie(None),
):
    if user_info:
        username = username_email_resol(user_info)
        mdb = m_db.connect_mdb()
        mdb = mdb["nlb"]
        update_status = None
        if m_db.q_status(db=mdb, username=username):
            update_status = " "

        # Query entire user books - Inefficient
        query = s_db.q_user_bks(username=username)
        response = p.process_user_bks(query)
        all_unique_books = p.get_unique_bks(response)
        all_avail_books = p.get_avail_bks(response)

        if library != "all":
            output = []
            for book in response:
                if library in book["BranchName"].lower():
                    output.append(book)
        else:
            output = response

        lib_avail = len(p.get_avail_bks(output))
        lib_all = len(p.get_unique_bks(output))

        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "username": username,
                "api_data": output,
                "library": library,
                "all_avail_books": all_avail_books,
                "all_unique_books": all_unique_books,
                "lib_avail": lib_avail,
                "lib_all": lib_all,
                "status": update_status,
            },
        )

    else:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)


def update_bk_avail_supa(db, bid_no: str):
    """
    - Takes in single BID to get avail info
    - Processes data for Supabase
    - Delete existing Supabase data if necessary
    - Inject new data into Supabase
    """
    try:
        # Make API call on book availability
        bk = n_api.get_bk_data("GetAvailabilityInfo", input_dict={"BRN": bid_no})
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
async def update_book(BID: str, db=Depends(get_db)):
    api_result = update_bk_avail_supa(db, BID)
    if api_result.get("API call"):
        return RedirectResponse("/main", status_code=status.HTTP_302_FOUND)


@app.post("/update_user_bks/", response_class=HTMLResponse)
async def update_user_bks(
    background_tasks: BackgroundTasks, db=Depends(get_db), user_info: str = Cookie(None)
):
    username = username_email_resol(user_info)
    mdb = m_db.connect_mdb()
    mdb = mdb["nlb"]
    m_db.insert_status(mdb, username=username)
    m_db.update_user_info(mdb, username, {"books_updated": 0})

    """ Updates availability of all user's saved books """
    background_tasks.add_task(update_all_user_bks, db, user_info)
    return RedirectResponse("/lib/all", status_code=status.HTTP_302_FOUND)


def update_all_user_bks(db, user_info):
    """Update all books linked to user."""
    username = username_email_resol(user_info)
    user_bids = s_db.q_user_bks_bids(db=db, username=username)
    user_bks_info = s_db.q_user_bks_info(username=username)

    mdb = m_db.connect_mdb()
    mdb = mdb["nlb"]
    for i, bk in enumerate(user_bks_info):
        bid_no = bk.get("BID")
        title = bk.get("TitleName")
        time.sleep(2)
        update_bk_avail_supa(db, bid_no)

        m_db.update_user_info(mdb, username, {"books_updated": i + 1, "title": title})
    m_db.delete_status(mdb, username=username)
    return {"message": "All user books updated!"}


@app.get("/book_status/{book_saved}")
async def book_status_progress_bar(
    request: Request, book_saved: int, db=Depends(get_db), user_info: str = Cookie(None)
):
    try:
        username = username_email_resol(user_info)
        mdb = m_db.connect_mdb()
        mdb = mdb["nlb"]
        user_info = m_db.q_user_info(db=mdb, username=username)
        books_updated = user_info.get("books_updated")
        title = user_info.get("title")

        print(books_updated)
        print(title)

        progress = 0
        if books_updated > 0:
            progress = (books_updated / book_saved) * 100

        update_status = None
        if m_db.q_status(db=mdb, username=username):
            update_status = " "

        return templates.TemplateResponse(
            "/partials/update_status_text.html",
            {
                "request": request,
                "progress": progress,
                "TitleName": title,
                "total_books": book_saved,
                "book_count": books_updated,
                "status": update_status,
            },
        )
    except:
        return templates.TemplateResponse(
            "/partials/update_status_text.html",
            {
                "request": request,
            },
        )


@app.post("/complete-update/", response_class=HTMLResponse)
async def update_book(request: Request):
    return templates.TemplateResponse("complete-status.html", {"request": request})


@app.get("/update_header", response_class=HTMLResponse)
async def update_header(
    request: Request, db=Depends(get_db), user_info: str = Cookie(None)
):
    username = username_email_resol(user_info)
    query = s_db.q_user_bks(username=username)
    response = p.process_user_bks(query)

    # Processing necessary statistics
    all_unique_books = p.get_unique_bks(response)
    all_avail_books = p.get_avail_bks(response)
    unique_libs = p.get_unique_libs(response)
    avail_bks_by_lib = p.get_avail_bks_by_lib(response)
    lib_book_summary = p.get_lib_bk_summary(unique_libs, avail_bks_by_lib)

    mdb = m_db.connect_mdb()
    mdb = mdb["nlb"]
    update_status = None
    if m_db.q_status(db=mdb, username=username):
        update_status = " "

    # Check if user has a default library
    user_info = s_db.q_user_info(db, username)
    preferred_lib = user_info.get("preferred_lib")

    if preferred_lib:
        preferred_lib = preferred_lib.lower()
        output = []
        for book in response:
            if preferred_lib in book["BranchName"].lower():
                output.append(book)

    else:
        preferred_lib = "all"
        output = response

    lib_avail = len(p.get_avail_bks(output))
    lib_all = len(p.get_unique_bks(output))

    return templates.TemplateResponse(
        "navbar.html",
        {
            "request": request,
            "username": username,
            "api_data": output,
            "all_avail_books": all_avail_books,
            "all_unique_books": all_unique_books,
            "avail_books": avail_bks_by_lib,
            "lib_book_summary": lib_book_summary,
            "lib_avail": lib_avail,
            "lib_all": lib_all,
            "library": preferred_lib,
            "status": update_status,
        },
    )


@app.post("/ingest_books_navbar", response_class=HTMLResponse)
async def ingest_books_navbar(
    request: Request,
    bids: list = Form(...),
    db=Depends(get_db),
    user_info: str = Cookie(None),
):
    username = username_email_resol(user_info)
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

    return templates.TemplateResponse(
        "navbar.html",
        {
            "request": request,
            "username": username,
            "all_avail_books": all_avail_books,
            "all_unique_books": all_unique_books,
            "lib_book_summary": lib_book_summary,
        },
    )


@app.delete("/delete_bk/{bid}", response_class=HTMLResponse)
async def delete_bk(
    request: Request, bid: int, db=Depends(get_db), user_info: str = Cookie(None)
):
    username = username_email_resol(user_info)
    final_count = s_db.q_bid_counter(bid_no=str(bid))

    # If book is only linked to one user,
    # delete book available and info records
    if final_count == 1:
        s_db.delete_bk_avail(db=db, bid_no=bid)
        s_db.delete_bk_info(db=db, bid_no=bid)
    s_db.delete_user_bk(db=db, username=username, bid_no=bid)

    return ""


@app.post("/delete_bks", response_class=HTMLResponse)
async def delete_bks(
    request: Request,
    bids: list = Form(...),
    db=Depends(get_db),
    user_info: str = Cookie(None),
):
    username = username_email_resol(user_info)
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

    return templates.TemplateResponse(
        "user_bks.html",
        {
            "request": request,
            "username": username,
            "api_data": output,
            "all_avail_books": all_avail_books,
            "all_unique_books": all_unique_books,
            "lib_book_summary": lib_book_summary,
        },
    )


@app.get("/profile", response_class=HTMLResponse)
async def user_profile(
    request: Request, db=Depends(get_db), user_info: str = Cookie(None)
):
    username = username_email_resol(user_info)
    query = s_db.q_user_bks(username=username)
    response = p.process_user_bks(query)
    unique_libs = p.get_unique_libs(response)
    mdb = m_db.connect_mdb()
    mdb = mdb["nlb"]
    update_status = None
    if m_db.q_status(db=mdb, username=username):
        update_status = " "

    # Query user profile info from database
    user_info = s_db.q_user_info(db, username)
    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "username": username,
            "email_address": user_info.get("email_address", None),
            "preferred_lib": user_info.get("preferred_lib", None),
            "pw_qn": user_info.get("pw_qn", None),
            "pw_ans": user_info.get("pw_ans", None),
            "all_unique_lib": unique_libs,
            "status": update_status,
        },
    )


@app.post("/update_user", response_class=HTMLResponse)
async def update_user(
    request: Request,
    email_address: str = Form(None),
    preferred_lib: str = Form(None),
    pw_qn: str = Form(None),
    pw_ans: str = Form(None),
    password: str = Form(None),
    db=Depends(get_db),
    user_info: str = Cookie(None),
):
    username = username_email_resol(user_info)
    # Update info
    new_dict = {
        "email_address": email_address,
        "preferred_lib": preferred_lib,
        "pw_qn": pw_qn,
        "pw_ans": pw_ans,
    }
    if password:
        hashed_password = get_hashed_password(password)
        new_dict.update({"HashedPassword": hashed_password})

    s_db.update_user_info(db, username, new_dict)
    return RedirectResponse(f"/profile", status_code=status.HTTP_302_FOUND)


@app.post("/delete_user", response_class=HTMLResponse)
async def delete_user(
    request: Request, db=Depends(get_db), user_info: str = Cookie(None)
):
    username = username_email_resol(user_info)
    s_db.delete_user(db, username=username)
    return RedirectResponse("/logout", status_code=status.HTTP_302_FOUND)


# Main Page
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("google_page.html", {"request": request})


# Logout route to remove the JWT token
@app.get("/logout")
def logout():
    response = RedirectResponse("/")
    response.delete_cookie("user_info")
    return response
