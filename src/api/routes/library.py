from typing import Optional

from fastapi import APIRouter, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from src import m_db
from src.api.deps import MDBDep, SDBDep, UsernameDep
from src.crud.book_avail import book_avail_crud
from src.crud.book_info import book_info_crud
from src.crud.users import user_crud
from src.modals.book_response import BookResponse
from src.utils import templates


router = APIRouter()


@router.get("/{library}", response_class=HTMLResponse)
async def show_avail_bks(
    request: Request,
    library: Optional[str],
    db: SDBDep,
    mdb: MDBDep,
    username: UsernameDep,
):
    if not username:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    # Query entire user books - Inefficient
    if not library:
        library = "all"

    # Get user_info if avail. Else redirect for proper sign-up
    user_info = await user_crud.get(db, i=username)
    if not user_info:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    # Extract user book info and compute book responses
    book_infos = await book_info_crud.get_multi_by_owner(db=db, username=username)
    book_avails = await book_avail_crud.get_multi_by_owner(
        db=db, username=username, BIDs=[book_info.BID for book_info in book_infos]
    )
    book_response = BookResponse(
        book_infos=book_infos, book_avails=book_avails, library=library
    )

    update_status = None
    if m_db.q_status(db=mdb.nlb, username=username):
        update_status = " "

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "username": username,
            "api_data": book_response.api_data,
            "library": library,
            "all_avail_books": book_response.all_avail_books,
            "all_unique_books": book_response.all_unique_books,
            "lib_avail": len(book_response.lib_avail_books),
            "lib_all": len(book_response.lib_all_books),
            "status": update_status,
        },
    )
