import re
from typing import Optional

from fastapi import APIRouter, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse


from src.api.deps import SDBDep, MDBDep, UsernameDep
from src import supa_db as s_db
from src import m_db
from src import process as p
from src import nlb_api as n_api
from src.utils import templates


router = APIRouter()


@router.get("", response_class=HTMLResponse)
async def search_books(
    request: Request,
    mdb: MDBDep,
    username: UsernameDep,
    book_search: Optional[str] = None,
    author: Optional[str] = None,
):
    if not username:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    # TODO: Figure out usage of q_status and deprecate if possible
    update_status = None
    if m_db.q_status(db=mdb.nlb, username=username):
        update_status = " "

    return templates.TemplateResponse(
        "search.html",
        {
            "request": request,
            "keyword": book_search,
            "author": author,
            "username": username,
            "status": update_status,
        },
    )


@router.get("/results", response_class=HTMLResponse)
async def htmx_search(
    request: Request,
    db: SDBDep,
    username: UsernameDep,
    e_resources: Optional[str] = None,
    book_search: Optional[str] = None,
    author: Optional[str] = None,
    offset: Optional[int] = 0,
):
    """Calls NLB API GetTitles Search and show results
    in search_table.html
    """
    if not username:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    if not book_search and not author:
        # return as no book_search or author is provided
        return

    bk_output = []
    search_input = dict(
        Title=re.sub(r"[^a-zA-Z0-9\s]", " ", book_search) if book_search else None,
        Author=re.sub(r"[^a-zA-Z0-9\s]", " ", author) if author else None,
    )

    # Get titles from NLB API
    titles = n_api.get_bk_data(
        ext_url="GetTitles", input_dict=search_input.copy(), offset=offset
    )
    if (
        titles.get("statusCode") in [400, 404, 500, 401, 405, 429]
        or titles.get("totalRecords") == 0
    ):
        # Return empty table
        # TODO: Display from NLP api to frontend if any
        return

    # Track user search in db
    s_db.user_search_tracking(
        db, table_name="user_search", username=username, search_params=search_input
    )

    total_records = titles.get("totalRecords", None)
    more_records = titles.get("hasMoreRecords", None)
    # BUG: Total_records does not tally as filterning is not done during API call
    pag_links = p.pg_links(offset, total_records)  # "all_unique_books": user_bids,.
    all_titles = p.process_title(titles)

    # Filter whether E-resources are included
    final_titles = list(
        filter(
            lambda t: t["type"] in ["Book"] + (["Ebook"] if e_resources else []),
            all_titles,
        )
    )
    # Search user book BIDs and disable add book if user saved the book
    user_books = s_db.q_user_bks(username=username)
    bid_checks = set(i.get("BID") for i in user_books)
    for bk in final_titles:
        bid = str(bk.get("BID") if bk.get("DigitalID") is None else bk.get("DigitalID"))
        title = bk.get("TitleName", " / ").split(" / ", 1)[0].strip()
        # Enable disable button if book is already saved
        disable = "disabled" if bid in bid_checks else ""
        bk["TitleName"] = title + " | " + bid
        bk["BID"] = disable + " | " + bid
        bk_output.append(bk)

    return templates.TemplateResponse(
        "partials/search_table.html",
        {
            "request": request,
            "keyword": book_search,
            "author": author,
            "username": username,
            "api_data": bk_output,
            "total_records": total_records,
            "more_records": more_records,
            "pag_links": pag_links,
            "e_resources": e_resources,
        },
    )
