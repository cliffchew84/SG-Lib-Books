import re
import time
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from nlb_catalogue_client.types import UNSET
from nlb_catalogue_client.api.catalogue import get_get_titles
from nlb_catalogue_client.models.get_titles_response_v2 import GetTitlesResponseV2


from src.api.deps import SDBDep, MDBDep, UsernameDep, NLBClientDep
from src import m_db
from src.crud.book_info import book_info_crud
from src.crud.user_search import user_search_crud
from src.modals.user_search import UserSearchCreate
from src.modals.title import Title
from src.utils import templates, pg_links


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
    nlb: NLBClientDep,
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
        # return as no book_search and author is provided
        return

    search_input = dict(
        Title=re.sub(r"[^a-zA-Z0-9\s]", " ", book_search) if book_search else None,
        Author=re.sub(r"[^a-zA-Z0-9\s]", " ", author) if author else None,
    )

    # Get titles from NLB API
    response = await get_get_titles.asyncio_detailed(
        client=nlb,
        title=search_input["Title"] if search_input["Title"] else UNSET,
        author=search_input["Author"] if search_input["Author"] else UNSET,
        offset=offset if offset else UNSET,
    )

    if (
        not isinstance(response.parsed, GetTitlesResponseV2)  # ErrorResponse
        or response.parsed.total_records == 0
    ):
        # Return empty table
        # TODO: Display from NLP api to frontend if any
        return

    # Track user search in db
    await user_search_crud.create(
        db,
        obj_in=UserSearchCreate(
            UserName=username,
            search_time=int(
                time.mktime(datetime.now().timetuple()),
            ),
            Title=search_input.get("Title", ""),
            Author=search_input.get("Author", ""),
        ),
    )

    total_records = response.parsed.total_records
    more_records = response.parsed.has_more_records
    # BUG: Total_records does not tally as filterning is not done during API call
    pag_links = pg_links(offset, total_records)  # "all_unique_books": user_bids,.
    all_titles = (
        [Title.from_nlb(t) for t in response.parsed.titles]
        if response.parsed.titles
        else []
    )

    # Filter whether E-resources are included
    final_titles = list(
        filter(
            lambda t: t.type in ["Book"] + (["Ebook"] if e_resources else []),
            all_titles,
        )
    )
    # Search user book BIDs and disable add book if user saved the book
    book_infos = await book_info_crud.get_multi_by_owner(db, username=username)
    bid_checks = set(str(book_info.BID) for book_info in book_infos)
    for bk in final_titles:
        bk.disabled = bk.BID in bid_checks

    return templates.TemplateResponse(
        "partials/search_table.html",
        {
            "request": request,
            "keyword": book_search,
            "author": author,
            "username": username,
            "api_data": [title.model_dump() for title in final_titles],
            "total_records": total_records,
            "more_records": more_records,
            "pag_links": pag_links,
            "e_resources": e_resources,
        },
    )
