from fastapi import APIRouter, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse


from src.api.deps import SDBDep, MDBDep, UsernameDep
from src import supa_db as s_db
from src import m_db
from src import process as p
from src.utils import templates


router = APIRouter()


@router.get("", response_class=HTMLResponse)
async def update_header(
    request: Request, db: SDBDep, mdb: MDBDep, username: UsernameDep
):
    if not username:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    query = s_db.q_user_bks(username=username)
    response = p.process_user_bks(query)

    # Processing necessary statistics
    all_unique_books = p.get_unique_bks(response)
    all_avail_books = p.get_avail_bks(response)
    unique_libs = p.get_unique_libs(response)
    avail_bks_by_lib = p.get_avail_bks_by_lib(response)
    lib_book_summary = p.get_lib_bk_summary(unique_libs, avail_bks_by_lib)

    update_status = None
    if m_db.q_status(db=mdb.nlb, username=username):
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
