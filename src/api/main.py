from fastapi import (
    APIRouter,
    status,
    Request,
)
from fastapi.responses import RedirectResponse, HTMLResponse

from src import m_db
from src import supa_db as s_db
from src import process as p
from src.api.deps import SDBDep, UsernameDep
from src.api.routes.auth import router as auth_router
from src.api.routes.books import router as books_router
from src.api.routes.library import router as library_router
from src.api.routes.nav import router as nav_router
from src.api.routes.search import router as search_router
from src.api.routes.user import router as user_router
from src.utils import templates

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(books_router, prefix="/books", tags=["books"])
api_router.include_router(library_router, prefix="/lib", tags=["lib"])
api_router.include_router(nav_router, prefix="/nav", tags=["nav"])
api_router.include_router(search_router, prefix="/search", tags=["search"])
api_router.include_router(user_router, prefix="/user", tags=["user"])


@api_router.get("/main", response_class=HTMLResponse)
async def main(request: Request, username: UsernameDep, db: SDBDep):
    if not username:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

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


# Main Page
@api_router.get("/", response_class=HTMLResponse)
async def root(request: Request, username: UsernameDep):
    if username:
        # Redirect to main if user is logged in
        return RedirectResponse("/main")
    return templates.TemplateResponse("google_page.html", {"request": request})
