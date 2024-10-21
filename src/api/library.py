from typing import Optional

from fastapi import APIRouter, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse


from src.api.deps import MDBDep, UsernameDep
from src import supa_db as s_db
from src import m_db
from src import process as p
from src.utils import templates


router = APIRouter()


@router.get("/{library}", response_class=HTMLResponse)
async def show_avail_bks(
    request: Request, library: Optional[str], mdb: MDBDep, username: UsernameDep
):
    if not username:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    update_status = None
    if m_db.q_status(db=mdb.nlb, username=username):
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

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "username": username,
            "api_data": output,
            "library": library,
            "all_avail_books": all_avail_books,
            "all_unique_books": all_unique_books,
            "lib_avail": len(p.get_avail_bks(output)),
            "lib_all": len(p.get_unique_bks(output)),
            "status": update_status,
        },
    )
