from collections import defaultdict

import asyncio
from fastapi import APIRouter, status, HTTPException
from google.cloud import tasks_v2
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

from src.api.deps import (
    CloudTaskDep,
    SDBDep,
    CurrentUser,
    NLBClientDep,
    NLBClientsDep,
    MessagingDep,
)
from src.config import settings
from src.crud.book_avail import book_avail_crud
from src.crud.book_info import book_info_crud
from src.crud.book_outdated_bid import book_outdated_bid_crud
from src.crud.book_subscription import book_subscription_crud
from src.crud.email_items import email_items_crud
from src.crud.notifications import notification_crud
from src.crud.notification_tokens import notification_token_crud
from src.crud.users import user_crud
from src.modals.book_avail import BookAvail, BookAvailCreate
from src.modals.book_info import BookInfoCreate
from src.modals.book_response import BookResponse
from src.modals.email_items import EmailItemsCreate
from src.modals.notifications import NotificationCreate
from src.services.firebase_messaging import FirebaseMessaging
from src.utils.book_avail import get_newly_available_books

router = APIRouter()


@router.get("")
async def get_books(
    user: CurrentUser,
    db: SDBDep,
) -> list[BookResponse]:
    """Get all books that user marked as favourite"""
    if not user or not user.email:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email is not found for user")

    try:
        book_infos = await book_info_crud.get_multi_by_owner(db, email=user.email)
        return [
            BookResponse(
                **book_info.model_dump(),
                avails=await book_avail_crud.get_multi_by_owner(
                    db, email=user.email, BIDs=[book_info.BID]
                ),
            )
            for book_info in book_infos
        ]

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Error occured with database transaction.",
        ) from e


@router.get("/{bid}")
async def get_book(
    bid: int, user: CurrentUser, db: SDBDep, nlb: NLBClientDep, live: bool = False
) -> BookResponse:
    if not user or not user.email:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email is not found for user")

    book_saved = True  # Book was saved before in database
    try:
        book_info = await book_info_crud.get(db, i=str(bid))
        if not book_info:
            book_saved = False
            # Book infomation does not exist in database,
            # querying from NLB API instead
            response_info = await get_get_title_details.asyncio_detailed(
                client=nlb, brn=bid
            )
            if not isinstance(response_info.parsed, GetTitleDetailsResponseV2):
                if response_info.status_code == 404:
                    raise HTTPException(
                        status.HTTP_404_NOT_FOUND, str(response_info.parsed)
                    )
                if response_info.status_code == 429:
                    raise HTTPException(
                        status.HTTP_429_TOO_MANY_REQUESTS, "Rate limited by NLB API"
                    )

                raise HTTPException(
                    status.HTTP_500_INTERNAL_SERVER_ERROR, str(response_info.parsed)
                )

            book_info = BookInfoCreate.from_nlb(response_info.parsed)

        if book_saved and not live:
            # If book was saved, its availiblity exists in database
            # If fetch_live param is set, live data will be queries regardless
            book_avail = await book_avail_crud.get_multi_by_owner(
                db, email=user.email, BIDs=[bid]
            )
        else:
            print("Querying live:")
            # Book availablitiy does not exist in database,
            # querying from NLB API instead
            response_avail = await get_get_availability_info.asyncio_detailed(
                client=nlb, brn=bid
            )
            if not isinstance(
                response_avail.parsed, GetAvailabilityInfoResponseV2
            ):  # ErrorResponse
                if response_avail.status_code == 429:
                    raise HTTPException(
                        status.HTTP_429_TOO_MANY_REQUESTS, "Rate limited by NLB API"
                    )
                if response_avail.status_code == 404:
                    # Book availibity does not exist, continues as book_avail is None
                    pass

                raise HTTPException(
                    status.HTTP_500_INTERNAL_SERVER_ERROR, str(response_avail.parsed)
                )

            book_avail = [
                BookAvailCreate.from_nlb(item)
                for item in response_avail.parsed.items or []
            ]

            # Save book avail to db if book was saved before
            if book_saved:
                await book_avail_crud.upsert(db, obj_ins=book_avail)

        return BookResponse(**book_info.model_dump(), avails=book_avail)

    except Exception as e:
        print(f"Error: {e}")
        if isinstance(e, HTTPException):
            raise e
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
) -> BookResponse:
    if not user or not user.email:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email is not found for user")

    # Makes API to bk info and bk avail
    response_info = await get_get_title_details.asyncio_detailed(client=nlb, brn=bid)
    if not isinstance(response_info.parsed, GetTitleDetailsResponseV2):
        if response_info.status_code == 404:
            raise HTTPException(status.HTTP_404_NOT_FOUND, str(response_info.parsed))
        if response_info.status_code == 429:
            raise HTTPException(
                status.HTTP_429_TOO_MANY_REQUESTS, "Rate limited by NLB API"
            )

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
        if response_avail.status_code == 429:
            raise HTTPException(
                status.HTTP_429_TOO_MANY_REQUESTS, "Rate limited by NLB API"
            )

        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, str(response_avail.parsed)
        )

    # Do all the adding at the end, after everything is confirmed
    # Insert and Update if conflict on book availability
    try:
        book_info_result = BookInfoCreate.from_nlb(response_info.parsed)
        await book_info_crud.create_book_by_user(
            db,
            obj_in=book_info_result,
            email=user.email,
        )
        all_avail_bks = [
            BookAvailCreate.from_nlb(item) for item in response_avail.parsed.items or []
        ]
        await book_avail_crud.upsert(
            db,
            obj_ins=all_avail_bks,
        )
        return BookResponse(**book_info_result.model_dump(), avails=all_avail_bks)
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Error occured with database transaction.",
        ) from e


async def update_book_avail(
    db, nlb, messaging: FirebaseMessaging, bid_no: int
) -> list[BookAvail]:
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
        if response.status_code == 200:
            # If Book avail have no records
            raise HTTPException(status.HTTP_404_NOT_FOUND, str(response.parsed))

        if response.status_code == 429:
            raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, str(response.parsed))

        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(response.parsed))

    # Insert and Update if conflict on book availability
    try:
        # Check if book info exists in database
        book_info = await book_info_crud.get(db, i=str(bid_no))
        if not book_info:
            # Book infomation does not exist in database,
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, "Book information does not exist in database"
            )

        old_book_avails = await book_avail_crud.get_all_by_bid(db, bid=bid_no)
        new_book_avails = [
            BookAvailCreate.from_nlb(item) for item in response.parsed.items or []
        ]
        book_avail_changes = get_newly_available_books(old_book_avails, new_book_avails)

        # Retrieve all subscriptions for the book that is now available
        subscriptions = await book_subscription_crud.get_all_by_item_nos(
            db, itemNos=[book_avail.ItemNo for book_avail in book_avail_changes]
        )

        user_set = set()  # email
        # Create notification for each subscription
        for subscription in subscriptions:
            if subscription.email in user_set:
                # Skip if user has already been notified
                continue

            user = await user_crud.get(db, i=subscription.email)
            user_set.add(subscription.email)

            # Skip if user does not exist
            if not user:
                continue

            notification_create = NotificationCreate(
                title=f"{book_info.TitleName or 'New Book'} is now On-Shelf.",
                description=f"{book_info.TitleName or 'New Book'} is available in {', '.join([avail.BranchName for avail in book_avail_changes])}",
                action=f"/dashboard/books/{bid_no}",
                isRead=False,
                email=subscription.email,
            )

            # Save notification to database
            await notification_crud.create(db, obj_in=notification_create)

            # Send notification via FCM if user has enabled push notification
            fcm_tokens = await notification_token_crud.get_multi_by_owner(
                db, email=subscription.email
            )
            if user.channel_push and fcm_tokens:
                fcm_res = messaging.send_messages(
                    tokens=[token.token for token in fcm_tokens],
                    title=notification_create.title,
                    body=notification_create.description or "",
                    data={
                        "action": notification_create.action,
                    },
                )
                print(
                    f"Sent FCM message. Success: {fcm_res.success_count}, Failure: {fcm_res.failure_count}"
                )

            # Send notification via email if user has enabled daily email notification
            if user.channel_email:
                await email_items_crud.create(
                    db,
                    obj_in=EmailItemsCreate(
                        BID=bid_no,
                        TitleName=book_info.TitleName,
                        Author=book_info.Author,
                        cover_url=book_info.cover_url,
                        url=f"https://sg-lib-books.web.app/dashboard/books/{bid_no}",
                        BranchName=[avail.BranchName for avail in book_avail_changes],
                        email=subscription.email,
                    ),
                )
                print("Email notification staged")

        book_avails = await book_avail_crud.upsert(
            db,
            obj_ins=new_book_avails,
        )
    except Exception as e:
        print(f"Error: {e}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Error occured with database transaction.",
        ) from e
    return book_avails


@router.put("", status_code=status.HTTP_204_NO_CONTENT)
async def update_books(
    db: SDBDep,
    nlbs: NLBClientsDep,
    user: CurrentUser,
    messaging: MessagingDep,
):
    """Updates availability of all saved books"""

    if user != "super" and user is not None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Only service account can Update all books",
        )

    # outdated_books = await book_outdated_bid_crud.get_all(db)
    #
    # fail_bid = defaultdict(lambda: settings.MAX_UPDATE_ATTEMPTS)  # failed bids and retries
    # # for i, nlb in enumerate(nlbs):
    # for book in outdated_books:
    #      try:
    #         await update_book_avail(db, nlb, messaging, book.BID)
    #         print(f"Updated book BID: {book.BID}")
    #     except Exception as e:
    #         if isinstance(e, HTTPException):
    #             if e.status_code == 404:
    #                 # delete book avail from DB if no records was found on book
    #                 await book_avail_crud.delete_by_bid(db, bid=book.BID)
    #
    #         print(f"Update fail for BID:{book.BID}: Error {e}")
    #         fail_bid.append(book.BID)
    # print(f"Failed to update {len(fail_bid)} books")

    outdated_books = await book_outdated_bid_crud.get_all(db)

    num_nlbs = len(nlbs)
    failed_bids = []  # Collect BIDs that ultimately fail

    async def update_with_retries(book, nlb, max_attempts=settings.MAX_UPDATE_ATTEMPTS):
        attempt = 0
        while attempt < max_attempts:
            try:
                await update_book_avail(db, nlb, messaging, book.BID)
                print(f"Updated book BID: {book.BID} (attempt {attempt + 1})")
                return True
            except HTTPException as e:
                if e.status_code == 404:
                    # No book record found at upstream, remove from ours
                    await book_avail_crud.delete_by_bid(db, bid=book.BID)
                    print(f"Deleted local BID: {book.BID} due to 404 at source.")
                    return True  # Considered 'handled'
                if e.status_code == 429:
                    # Sleep for a while if rate limited
                    print(f"Rate limited for BID:{book.BID}, retrying...")
                else:
                    print(
                        f"Update fail for BID:{book.BID} HTTPException {e.status_code} (attempt {attempt + 1})"
                    )
            except Exception as e:
                print(
                    f"Update fail for BID:{book.BID}: Error {repr(e)} (attempt {attempt + 1})"
                )
            attempt += 1
            if attempt < max_attempts:
                await asyncio.sleep(0.5)
        return False  # Failed after all attempts

    # Parallelize book updates, assign NLBs round-robin
    update_tasks = []
    for i, book in enumerate(outdated_books):
        nlb = nlbs[i % num_nlbs]
        update_tasks.append(update_with_retries(book, nlb))

    results = await asyncio.gather(*update_tasks)

    # Collect failed bids (where result is False)
    failed_bids = [
        book.BID for book, success in zip(outdated_books, results) if not success
    ]
    if failed_bids:
        print(f"Failed to update {len(failed_bids)} books: {failed_bids}")
    else:
        print("All books updated successfully.")


@router.put("/{bid}")
async def update_book(
    bid: int, db: SDBDep, nlb: NLBClientDep, user: CurrentUser, messaging: MessagingDep
) -> list[BookAvail]:
    if not user or not user.email:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email is not found for user")

    book_avail = await update_book_avail(db, nlb, messaging, bid)
    return book_avail


@router.delete("/{bid}")
async def unlike_book(bid: int, db: SDBDep, user: CurrentUser):
    if not user or not user.email:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email is not found for user")

    # Get all book avail for given book
    book_avail = await book_avail_crud.get_all_by_bid(db, bid=bid)

    # Delete Book subscriptions for given books
    await book_subscription_crud.delete_by_owner_and_itemNo(
        db, email=user.email, itemNos=[book.ItemNo for book in book_avail]
    )

    # Delete book owner relationship
    await book_info_crud.delete_owner(db, i=str(bid), email=user.email)

    # Delete book if no more owner
    await book_info_crud.delete_if_no_owner(db, i=str(bid))
    return
