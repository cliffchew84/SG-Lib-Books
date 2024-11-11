from collections import defaultdict

from fastapi import APIRouter, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from src.api.deps import SDBDep, MDBDep, UsernameDep
from src.crud.users import user_crud
from src.crud.book_info import book_info_crud
from src.crud.book_avail import book_avail_crud
from src import m_db
from src.utils import templates

router = APIRouter()


@router.get("", response_class=HTMLResponse)
async def update_header(
    request: Request, db: SDBDep, mdb: MDBDep, username: UsernameDep
):
    if not username:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    # Get user_info if avail. Else redirect for proper sign-up
    user_info = await user_crud.get(db, i=username)
    if not user_info:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    # Continue to extract user book info
    book_infos = await book_info_crud.get_multi_by_owner(db=db, username=username)
    book_avails = await book_avail_crud.get_multi_by_owner(
        db=db, username=username, BIDs=[book_info.BID for book_info in book_infos]
    )
    book_info_dict = {book_info.BID: book_info for book_info in book_infos}
    api_data = [
        {**book_avail.model_dump(), **book_info_dict[book_avail.BID].model_dump()}
        for book_avail in book_avails
    ]

    # Processing necessary statistics
    all_unique_books = [
        book_info.TitleName for book_info in book_infos
    ]  # List of book title
    all_avail_books = [
        book_info
        for book_info in book_infos
        if book_info.BID
        in {
            book_avail.BID
            for book_avail in book_avails
            if book_avail.StatusDesc == "Available"
        }
    ]  # List of book_info if book is available
    all_avail_book_title = [
        book_info.TitleName for book_info in all_avail_books
    ]  # List of book title if book is available
    book_counter = defaultdict(int)
    for book_avail in book_avails:
        branchName = (
            book_avail.BranchName.replace("Public", "").replace("Library", "").strip()
        )
        book_counter[branchName] += 1 if book_avail.StatusDesc == "Available" else 0
    lib_book_summary = sorted(book_counter.items())  # List of (lib_name: count)

    # Count number of avail and all items in preferred lib if available
    preferred_lib = user_info.preferred_lib
    lib_avail_count = (
        len(
            [
                book_info
                for book_info in all_avail_books
                if book_info.BID
                in {
                    book_avail.BID
                    for book_avail in book_avails
                    if (
                        book_avail.BranchName.replace("Public", "")
                        .replace("Library", "")
                        .strip()
                        .lower()
                        == preferred_lib.lower()
                    )
                }
            ]
        )
        if preferred_lib is not None
        else len(all_avail_books)
    )
    lib_all_count = (
        len(
            [
                book_info
                for book_info in book_infos
                if book_info.BID
                in {
                    book_avail.BID
                    for book_avail in book_avails
                    if (
                        book_avail.BranchName.replace("Public", "")
                        .replace("Library", "")
                        .strip()
                        .lower()
                        == preferred_lib.lower()
                    )
                }
            ]
        )
        if preferred_lib is not None
        else len(book_infos)
    )

    update_status = None
    if m_db.q_status(db=mdb.nlb, username=username):
        update_status = " "

    return templates.TemplateResponse(
        "navbar.html",
        {
            "request": request,
            "username": username,
            "api_data": api_data,
            "all_avail_books": all_avail_book_title,
            "all_unique_books": all_unique_books,
            "avail_books": all_avail_books,
            "lib_book_summary": lib_book_summary,
            "lib_avail": lib_avail_count,
            "lib_all": lib_all_count,
            "library": preferred_lib,
            "status": update_status,
        },
    )
