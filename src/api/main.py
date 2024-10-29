from collections import Counter

from fastapi import (
    APIRouter,
    status,
    Request,
)
from fastapi.responses import RedirectResponse, HTMLResponse

from src import m_db
from src.api.deps import MDBDep, SDBDep, UsernameDep
from src.api.routes.auth import router as auth_router
from src.api.routes.books import router as books_router
from src.api.routes.library import router as library_router
from src.api.routes.nav import router as nav_router
from src.api.routes.search import router as search_router
from src.api.routes.user import router as user_router
from src.crud.book_avail import book_avail_crud
from src.crud.book_info import book_info_crud
from src.crud.users import user_crud
from src.utils import templates

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(books_router, prefix="/books", tags=["books"])
api_router.include_router(library_router, prefix="/lib", tags=["lib"])
api_router.include_router(nav_router, prefix="/nav", tags=["nav"])
api_router.include_router(search_router, prefix="/search", tags=["search"])
api_router.include_router(user_router, prefix="/user", tags=["user"])


@api_router.get("/main", response_class=HTMLResponse)
async def main(request: Request, username: UsernameDep, db: SDBDep, mdb: MDBDep):
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
    lib_book_summary = Counter(
        [
            book_avail.BranchName.replace("Public", "").replace("Library", "").strip()
            for book_avail in book_avails
            if book_avail.StatusDesc == "Available"
        ]
    ).items()  # List of (lib_name: count)

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
        "main.html",
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


# Main Page
@api_router.get("/", response_class=HTMLResponse)
async def root(request: Request, username: UsernameDep):
    if username:
        # Redirect to main if user is logged in
        return RedirectResponse("/main")
    return templates.TemplateResponse("google_page.html", {"request": request})
