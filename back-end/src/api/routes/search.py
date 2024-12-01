import time
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from nlb_catalogue_client.types import UNSET
from nlb_catalogue_client.api.catalogue import get_search_titles
from nlb_catalogue_client.models.search_titles_response_v2 import SearchTitlesResponseV2


from src.api.deps import SDBDep, UsernameDep, NLBClientDep
from src.crud.user_search import user_search_crud
from src.modals.book_info import BookInfo
from src.modals.book_search import SearchResponse
from src.modals.user_search import UserSearchCreate


router = APIRouter()


@router.get("")
async def search_books(
    db: SDBDep,
    nlb: NLBClientDep,
    username: UsernameDep,
    keyword: str = "",
    offset: Optional[int] = 0,
    limit: Optional[int] = 25,
) -> SearchResponse:
    """Calls NLB API GetTitles Search and show results
    in search_table.html
    """
    if not username:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User is unauthorized")

    if not keyword:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Keyword is empty in params")

    # Get titles from NLB API
    response = await get_search_titles.asyncio_detailed(
        client=nlb,
        keywords=keyword,
        offset=offset if offset else UNSET,
        limit=limit if limit else UNSET,
    )

    # Raise error if NLB API throw error
    if not isinstance(response.parsed, SearchTitlesResponseV2):
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(response.parsed))

    # Return 404 if no response is found
    if response.parsed.total_records == 0 or not response.parsed.titles:
        # Return empty table
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No search results are found")

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

    total_records = (
        response.parsed.total_records if response.parsed.total_records else 0
    )
    has_more_records = (
        response.parsed.has_more_records if response.parsed.has_more_records else False
    )
    next_offset = (offset if offset else 0) + (limit if limit else 0)

    return SearchResponse(
        total_records=total_records,
        has_more_records=has_more_records,
        next_offset=next_offset,
        titles=[BookInfo.from_search(title) for title in response.parsed.titles],
    )
