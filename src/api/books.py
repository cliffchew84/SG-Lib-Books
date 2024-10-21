import time

from fastapi import APIRouter, BackgroundTasks, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse


from src.api.deps import SDBDep, MDBDep, UsernameDep
from src import supa_db as s_db
from src import m_db
from src import nlb_api as n_api
from src import process as p
from src.utils import templates


router = APIRouter()


def update_bk_avail_supa(db, bid_no: str) -> bool:
    """
    - Takes in single BID to get avail info
    - Processes data for Supabase
    - Delete existing Supabase data if necessary
    - Inject new data into Supabase
    """
    try:
        # Make API call on book availability
        bk = n_api.get_bk_data("GetAvailabilityInfo", input_dict={"BRN": bid_no})
        all_avail_bks = [p.process_bk_avail(i) for i in bk.get("items", [])]

        if len(all_avail_bks) == 0:
            return False

        # TODO: User update_bk_avail instead
        s_db.delete_bk_avail(db=db, bid_no=bid_no)
        s_db.add_avail_bks(db=db, books_avail=all_avail_bks)

    except Exception:
        return False

    return True


@router.get("")
async def get_books(request: Request, username: UsernameDep, mdb: MDBDep):
    """Render user books within main_content"""

    if username is None:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    update_status = m_db.q_status(db=mdb.nlb, username=username)
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


def update_all_user_bks(db, mdb, username):
    """Update all books linked to user."""
    user_bks_info = s_db.q_user_bks_info(username=username)

    for i, bk in enumerate(user_bks_info):
        bid_no = bk.get("BID")
        title = bk.get("TitleName")
        time.sleep(2)
        update_bk_avail_supa(db, bid_no)

        m_db.update_user_info(mdb, username, {"books_updated": i + 1, "title": title})
    m_db.delete_status(mdb, username=username)
    return {"message": "All user books updated!"}


@router.post("", response_class=HTMLResponse)
async def ingest_books_navbar(
    request: Request,
    db: SDBDep,
    username: UsernameDep,
    bids: list = Form(...),
):
    if username is None:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    for bid in bids:
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


@router.put("", response_class=HTMLResponse)
async def update_books(
    background_tasks: BackgroundTasks, db: SDBDep, mdb: MDBDep, username: UsernameDep
):
    """Updates availability of all user's saved books"""
    if not username:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    m_db.insert_status(mdb.nlb, username=username)
    m_db.update_user_info(mdb.nlb, username, {"books_updated": 0})

    # Set background task to query and update all user's books
    background_tasks.add_task(update_all_user_bks, db, mdb.nlb, username)

    # Redirect to library all page
    return RedirectResponse("/lib/all", status_code=status.HTTP_302_FOUND)


@router.put("/{BID}", response_class=HTMLResponse)
async def update_book(BID: str, db: SDBDep):
    success = update_bk_avail_supa(db, BID)
    if success:
        return RedirectResponse("/main", status_code=status.HTTP_302_FOUND)


@router.delete("/{BID}", response_class=HTMLResponse)
async def delete_book(BID: int, db: SDBDep, username: UsernameDep):
    if not username:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    final_count = s_db.q_bid_counter(bid_no=BID)

    # If book is only linked to one user,
    # delete book available and info records
    if final_count == 1:
        s_db.delete_bk_avail(db=db, bid_no=BID)
        s_db.delete_bk_info(db=db, bid_no=BID)
    s_db.delete_user_bk(db=db, username=username, bid_no=BID)

    return ""
