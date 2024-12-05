from fastapi import APIRouter, BackgroundTasks, status, HTTPException
from nlb_catalogue_client.api.catalogue import (
    get_get_availability_info,
    get_get_title_details,
)
from nlb_catalogue_client.models.get_availability_info_response_v2 import (
    GetAvailabilityInfoResponseV2,
)
from nlb_catalogue_client.models.get_title_details_response_v2 import (
    GetTitleDetailsResponseV2,
)

from src.api.deps import SDBDep, CurrentUser, NLBClientDep
from src.crud.book_avail import book_avail_crud
from src.crud.book_info import book_info_crud
from src.modals.book_avail import BookAvail, BookAvailCreate
from src.modals.book_info import BookInfoCreate
from src.modals.book_response import BookResponse

router = APIRouter()


@router.get("")
async def get_books(
    user: CurrentUser,
    db: SDBDep,
) -> list[BookResponse]:
    """Get all books that user marked as favourite"""
    if not user.email:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email is not found for user")

    try:
        book_infos = await book_info_crud.get_multi_by_owner(db, username=user.email)
        return [
            BookResponse(
                **book_info.model_dump(),
                avails=await book_avail_crud.get_multi_by_owner(
                    db, username=user.email, BIDs=[book_info.BID]
                ),
            )
            for book_info in book_infos
        ]

    except Exception as e:
        print(e)
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Error occured with database transaction.",
        ) from e


@router.get("/{bid}")
async def get_book(
    bid: int,
    user: CurrentUser,
    db: SDBDep,
) -> BookResponse:
    if not user.email:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email is not found for user")

    try:
        book_info = await book_info_crud.get(db, i=str(bid))
        if not book_info:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, f"Book brn: {bid} is not found in database"
            )
        book_avail = await book_avail_crud.get_multi_by_owner(
            db, username=user.email, BIDs=[bid]
        )

        return BookResponse(**book_info.model_dump(), avails=book_avail)

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        print(e)
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Error occured with database transaction.",
        ) from e


@router.post("/{bid}", status_code=status.HTTP_201_CREATED)
async def like_book(
    bid: int,
    db: SDBDep,
    nlb: NLBClientDep,
    user: CurrentUser,
) -> None:
    if not user.email:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email is not found for user")

    # Makes API to bk info and bk avail
    response_info = await get_get_title_details.asyncio_detailed(client=nlb, brn=bid)
    if not isinstance(response_info.parsed, GetTitleDetailsResponseV2):
        if response_info.status_code == 404:
            raise HTTPException(status.HTTP_404_NOT_FOUND, str(response_info.parsed))
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, str(response_info.parsed)
        )

    response_avail = await get_get_availability_info.asyncio_detailed(
        client=nlb, brn=bid
    )
    if (
        not isinstance(
            response_avail.parsed, GetAvailabilityInfoResponseV2
        )  # ErrorResponse
        or response_avail.parsed.total_records == 0
    ):
        # Return empty table
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, str(response_avail.parsed)
        )

    # Do all the adding at the end, after everything is confirmed
    # Insert and Update if conflict on book availability
    try:
        await book_info_crud.create_book_by_user(
            db,
            obj_in=BookInfoCreate.from_nlb(response_info.parsed),
            username=user.email,
        )
        all_avail_bks = [
            BookAvailCreate.from_nlb(item) for item in response_avail.parsed.items or []
        ]
        await book_avail_crud.upsert(
            db,
            obj_ins=all_avail_bks,
        )
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Error occured with database transaction.",
        ) from e


async def update_book_avail(db, nlb, bid_no: int) -> list[BookAvail]:
    """
    - Takes in single BID to get avail info
    - Processes data for Supabase
    - Delete existing Supabase data if necessary
    - Inject new data into Supabase
    """

    # Make API call on book availability
    response = await get_get_availability_info.asyncio_detailed(client=nlb, brn=bid_no)
    if (
        not isinstance(response.parsed, GetAvailabilityInfoResponseV2)  # ErrorResponse
        or response.parsed.total_records == 0
    ):
        # Return empty table
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(response.parsed))

    # Inser and Update if conflict on book availability
    try:
        all_avail_bks = [
            BookAvailCreate.from_nlb(item) for item in response.parsed.items or []
        ]
        book_avails = await book_avail_crud.upsert(
            db,
            obj_ins=all_avail_bks,
        )
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Error occured with database transaction.",
        ) from e
    return book_avails


@router.put("")
async def update_books(
    background_tasks: BackgroundTasks,
    db: SDBDep,
    nlb: NLBClientDep,
    user: CurrentUser,
):
    """Updates availability of all user's saved books"""
    if not user.email:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email is not found for user")

    async def update_all_books(bids: list[int]) -> None:
        for bid in bids:
            await update_book_avail(db, nlb, bid)

    try:
        book_infos = await book_info_crud.get_multi_by_owner(db, username=user.email)

        # Set background task to query and update all user's books
        background_tasks.add_task(
            update_all_books, [book_info.BID for book_info in book_infos]
        )

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        print(e)
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Error occured with database transaction.",
        ) from e


@router.put("/{bid}")
async def update_book(bid: int, db: SDBDep, nlb: NLBClientDep) -> list[BookAvail]:
    book_avail = await update_book_avail(db, nlb, bid)
    return book_avail


@router.delete("/{bid}")
async def unlike_book(bid: int, db: SDBDep, user: CurrentUser):
    if not user.email:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email is not found for user")

    bid_no = str(bid)

    await book_info_crud.delete_owner(db, i=bid_no, username=user.email)
    return
