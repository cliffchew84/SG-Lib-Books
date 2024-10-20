import re
from typing import Optional

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse


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
    db: SDBDep,
    mdb: MDBDep,
    username: UsernameDep,
    book_search: Optional[str] = None,
    author: Optional[str] = None,
):
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
):
    """Calls NLB API GetTitles Search and show results
    in search_table.html
    """

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
        ext_url="GetTitles", input_dict=search_input.copy(), offset=0
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
    pag_links = p.pg_links(0, total_records)  # "all_unique_books": user_bids,.
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


#
#
# @app.get("/navigate_search", response_class=HTMLResponse)
# async def paginate_search(
#     request: Request,
#     book_search: Optional[str] = None,
#     author: Optional[str] = None,
#     offset: Optional[str] = None,
#     e_resources: Optional[str] = None,
#     db=SDBDep,
#     user_info: str = Cookie(None),
# ):
#     """Calls new GetTitles Search and show results in search_table.html"""
#     final_response, search_input = list(), dict()
#     username = username_email_resol(user_info)
#
#     if book_search:
#         c_book_search = re.sub(r"[^a-zA-Z0-9\s]", " ", book_search)
#         search_input.update({"Title": c_book_search})
#
#     if author:
#         c_author = re.sub(r"[^a-zA-Z0-9\s]", " ", author)
#         search_input.update({"Author": c_author})
#
#     if book_search or author:
#         titles = n_api.get_bk_data(
#             ext_url="GetTitles", input_dict=search_input, offset=offset
#         )
#         total_records = titles.get("totalRecords")
#         pag_links = p.pg_links(int(offset), total_records)
#
#         errors = [400, 404, 500, 401, 405, 429]
#         if titles.get("statusCode") in errors or titles.get("totalRecords") == 0:
#             # return empty table
#             return templates.TemplateResponse(
#                 "partials/search_table.html",
#                 {
#                     "request": request,
#                     "keyword": book_search,
#                     "author": author,
#                     "username": username,
#                     "api_data": final_response,
#                 },
#             )
#
#         else:
#             all_titles = p.process_title(titles)
#             more_records = titles.get("hasMoreRecords")
#
#             # Only keep physical books for now
#             final_titles = [t for t in all_titles if t["type"] == "Book"]
#
#             if e_resources:
#                 print("Including ebooks")
#                 ebooks = [t for t in all_titles if t["type"] == "Ebook"]
#                 final_titles += ebooks
#
#             # Search user book BIDs and disable add book if user saved the book
#             user_books = s_db.q_user_bks(username=username)
#             bid_checks = set(i.get("BID") for i in user_books)
#             for book in final_titles:
#                 # Prep for eResources in the future
#                 bid = (
#                     book.get("BID")
#                     if book.get("DigitalID") is None
#                     else book.get("DigitalID")
#                 )
#                 bid = str(bid)
#
#                 title = book.get("TitleName", "")
#                 title = title.split(" / ", 1)[0].strip()
#
#                 # Enable disable button if book is already saved
#                 disable = "disabled" if bid in bid_checks else ""
#
#                 book["TitleName"] = title + " | " + bid
#                 book["BID"] = disable + " | " + bid
#
#                 final_response.append(book)
#
#     return templates.TemplateResponse(
#         "partials/search_table.html",
#         {
#             "request": request,
#             "keyword": book_search,
#             "author": author,
#             "username": username,
#             "api_data": final_response,
#             "total_records": total_records,
#             "more_records": more_records,
#             "pag_links": pag_links,
#             "e_resources": e_resources,
#         },
#     )

# @app.post("/ingest_books_navbar", response_class=HTMLResponse)
# async def ingest_books_navbar(
#     request: Request,
#     bids: list = Form(...),
#     db=Depends(get_db),
#     user_info: str = Cookie(None),
# ):
#     username = username_email_resol(user_info)
#     for bid in bids:
#         print(bid)
#         # Makes API to bk info and bk avail and ingest the data into DB
#         bk_title = n_api.get_process_bk_info(bid_no=bid)
#
#         time.sleep(2)
#         update_bk_avail_supa(db, bid)
#
#         # Do all the adding at the end, after everything is confirmed
#         # This also doesn't require any time.sleep() as this is with my own DB
#         s_db.add_user_book(db=db, username=username, bid_no=bid)
#         s_db.add_book_info(db=db, books_info=bk_title)
#
#         print("print started book_available update")
#
#     # Update the books calculation on the navbar
#     query = s_db.q_user_bks(username=username)
#     response = p.process_user_bks(query)
#
#     # Processing necessary statistics
#     all_unique_books = p.get_unique_bks(response)
#     all_avail_books = p.get_avail_bks(response)
#     unique_libs = p.get_unique_libs(response)
#     avail_bks_by_lib = p.get_avail_bks_by_lib(response)
#     lib_book_summary = p.get_lib_bk_summary(unique_libs, avail_bks_by_lib)
#
#     return templates.TemplateResponse(
#         "navbar.html",
#         {
#             "request": request,
#             "username": username,
#             "all_avail_books": all_avail_books,
#             "all_unique_books": all_unique_books,
#             "lib_book_summary": lib_book_summary,
#         },
#     )
