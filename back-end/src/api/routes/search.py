import time
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import RedirectResponse
from nlb_catalogue_client.types import UNSET
from nlb_catalogue_client.api.catalogue import get_search_titles
from nlb_catalogue_client.models.search_titles_response_v2 import SearchTitlesResponseV2


from src.modals.book_info import BookInfo, BookInfoCreate
from src.api.deps import SDBDep, UsernameDep, NLBClientDep
from src.crud.user_search import user_search_crud
from src.modals.user_search import UserSearchCreate


router = APIRouter()


@router.get("")
async def search_books(
    db: SDBDep,
    nlb: NLBClientDep,
    username: UsernameDep,
    keyword: str = "",
    offset: Optional[int] = 0,
) -> list[BookInfo]:
    """Calls NLB API GetTitles Search and show results
    in search_table.html
    """
    if not username:
        raise HTTPException(401, "User is unauthorized")

    if not keyword:
        raise HTTPException(404, "Keyword is empty")

    # Get titles from NLB API
    response = await get_search_titles.asyncio_detailed(
        client=nlb,
        keywords=keyword,
        offset=offset if offset else UNSET,
    )

    if (
        not isinstance(response.parsed, SearchTitlesResponseV2)  # ErrorResponse
        or response.parsed.total_records == 0
        or not response.parsed.titles
    ):
        # Return empty table
        # TODO: Display from NLP api to frontend if any
        return []

    # Track user search in db
    await user_search_crud.create(
        db,
        obj_in=UserSearchCreate(
            UserName=username,
            search_time=int(
                time.mktime(datetime.now().timetuple()),
            ),
            Title=keyword,
            Author="",
        ),
    )

    total_records = response.parsed.total_records
    more_records = response.parsed.has_more_records

    return [BookInfo.from_search(title) for title in response.parsed.titles]
