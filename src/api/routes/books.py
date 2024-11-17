from fastapi import APIRouter, BackgroundTasks, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from nlb_catalogue_client.api.catalogue import (
    get_get_availability_info,
    get_get_title_details,
)
from nlb_catalogue_client.models.get_availability_info_response_v2 import (
    GetAvailabilityInfoResponseV2,
)
from nlb_catalogue_client.models.get_title_details_response_v2 import (
    GetTitleDetailsResponseV2,
)

from src import m_db
from src.api.deps import SDBDep, MDBDep, UsernameDep, NLBClientDep
from src.crud.book_avail import book_avail_crud
from src.crud.book_info import book_info_crud
from src.modals.book_avail import BookAvailCreate
from src.modals.book_info import BookInfoCreate
from src.modals.book_response import BookResponse
from src.utils import templates

router = APIRouter()


async def update_bk_avail_supa(db, nlb, bid_no: int) -> bool:
    """
    - Takes in single BID to get avail info
    - Processes data for Supabase
    - Delete existing Supabase data if necessary
    - Inject new data into Supabase
    """
    try:
        # Make API call on book availability
        response = await get_get_availability_info.asyncio_detailed(
            client=nlb, brn=bid_no
        )
        if (
            not isinstance(
                response.parsed, GetAvailabilityInfoResponseV2
            )  # ErrorResponse
            or response.parsed.total_records == 0
        ):
            # Return empty table
            # TODO: Display from NLP api to frontend if any
            return False
        all_avail_bks = [
            BookAvailCreate.from_nlb(item) for item in response.parsed.items or []
        ]

        if len(all_avail_bks) == 0:
            return False

        # Inser and Update if conflict on book availability
        await book_avail_crud.upsert(
            db,
            obj_ins=all_avail_bks,
        )

    except Exception as error:
        print(error)
        return False

    return True


async def update_all_user_bks(db, mdb, nlb, username):
    """Update all books linked to user."""
    book_infos = await book_info_crud.get_multi_by_owner(db, username=username)

    for i, bk in enumerate(book_infos):
        await update_bk_avail_supa(db, nlb, bk.BID)
        m_db.update_user_info(
            mdb, username, {"books_updated": i + 1, "title": bk.TitleName}
        )
    m_db.delete_status(mdb, username=username)
    return {"message": "All user books updated!"}


@router.get("")
async def get_books(request: Request, username: UsernameDep, db: SDBDep, mdb: MDBDep):
    """Render user books within main_content"""

    if username is None:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    update_status = m_db.q_status(db=mdb.nlb, username=username)
    book_infos = await book_info_crud.get_multi_by_owner(db, username=username)
    book_avails = await book_avail_crud.get_multi_by_owner(
        db, username=username, BIDs=[book_info.BID for book_info in book_infos]
    )
    book_response = BookResponse(book_infos=book_infos, book_avails=book_avails)

    return templates.TemplateResponse(
        "user_bks.html",
        {
            "request": request,
            "username": username,
            "api_data": book_response.book_infos_with_callnumber,
            "status": update_status,
        },
    )


@router.get("/status/{book_saved}")
async def book_status_progress_bar(
    request: Request, book_saved: int, mdb: MDBDep, username: UsernameDep
):
    if username is None:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    try:
        user_info = m_db.q_user_info(db=mdb.nlb, username=username)
        books_updated = user_info.get("books_updated") if user_info else None
        title = user_info.get("title") if user_info else None

        if books_updated is None or title is None:
            return templates.TemplateResponse(
                "/partials/update_status_text.html",
                {
                    "request": request,
                },
            )

        progress = 0
        if books_updated > 0:
            progress = (books_updated / book_saved) * 100

        update_status = None
        if m_db.q_status(db=mdb.nlb, username=username):
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
    except Exception:
        return templates.TemplateResponse(
            "/partials/update_status_text.html",
            {
                "request": request,
            },
        )


@router.get("/complete", response_class=HTMLResponse)
async def complete_update(request: Request):
    return templates.TemplateResponse("complete_status.html", {"request": request})


@router.post("", response_class=HTMLResponse)
async def ingest_books_navbar(
    request: Request,
    db: SDBDep,
    nlb: NLBClientDep,
    username: UsernameDep,
    bids: list = Form(...),
):
    if username is None:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    for bid in bids:
        # Makes API to bk info and bk avail and ingest the data into DB
        response = await get_get_title_details.asyncio_detailed(client=nlb, brn=bid)
        if not isinstance(response.parsed, GetTitleDetailsResponseV2):
            # TODO: Log error response
            continue

        # Do all the adding at the end, after everything is confirmed
        await book_info_crud.create_book_by_user(
            db,
            obj_in=BookInfoCreate.from_nlb(response.parsed),
            username=username,
        )

        await update_bk_avail_supa(db, nlb, bid)

        print("print started book_available update")

    # Update the books calculation on the navbar
    book_infos = await book_info_crud.get_multi_by_owner(db=db, username=username)
    book_avails = await book_avail_crud.get_multi_by_owner(
        db=db, username=username, BIDs=[book_info.BID for book_info in book_infos]
    )
    book_response = BookResponse(
        book_infos=book_infos, book_avails=book_avails, library="all"
    )

    return templates.TemplateResponse(
        "navbar.html",
        {
            "request": request,
            "username": username,
            "all_avail_books": book_response.all_avail_books,
            "all_unique_books": book_response.all_unique_books,
            "lib_book_summary": book_response.lib_book_summary,
        },
    )


@router.put("", response_class=HTMLResponse)
async def update_books(
    background_tasks: BackgroundTasks,
    db: SDBDep,
    mdb: MDBDep,
    nlb: NLBClientDep,
    username: UsernameDep,
):
    """Updates availability of all user's saved books"""
    if not username:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    m_db.insert_status(mdb.nlb, username=username)
    m_db.update_user_info(mdb.nlb, username, {"books_updated": 0})

    # Set background task to query and update all user's books
    background_tasks.add_task(update_all_user_bks, db, mdb.nlb, nlb, username)

    # Redirect to library all page
    return RedirectResponse("/lib/all", status_code=status.HTTP_303_SEE_OTHER)


@router.put("/{BID}", response_class=HTMLResponse)
async def update_book(BID: int, db: SDBDep, nlb: NLBClientDep):
    success = await update_bk_avail_supa(db, nlb, BID)
    if success:
        return RedirectResponse("/lib/all", status_code=status.HTTP_303_SEE_OTHER)


@router.delete("/{BID}", response_class=HTMLResponse)
async def delete_book(BID: int, db: SDBDep, username: UsernameDep):
    if not username:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    bid = str(BID)
    owners = await book_info_crud.get_owners(db, i=bid)

    # If book is only linked to one user,
    # delete book available and info records
    if len(owners) == 1:
        await book_avail_crud.delete(db, i=bid)
        await book_info_crud.delete(db, i=bid)
        return ""

    await book_info_crud.delete_owner(db, i=bid, username=username)
    return ""
