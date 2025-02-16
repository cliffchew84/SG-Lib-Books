from fastapi import APIRouter, status, HTTPException

from src.api.deps import SDBDep, CurrentUser
from src.crud.book_subscription import book_subscription_crud
from src.modals.book_subscription import (
    BookSubscription,
    BookSubscriptionCreate,
    BookSubscriptionUpdate,
)

router = APIRouter()


@router.get("/{bid}")
async def get_book_subscription(
    bid: str, db: SDBDep, user: CurrentUser
) -> list[BookSubscription]:
    """Get all book_subscription belonged to bid"""
    if not getattr(user, "email", None):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email is not found for user")

    try:
        book_subscription: list[
            BookSubscription
        ] = await book_subscription_crud.get_all_by_bid(db, bid=bid, email=user.email)
        return book_subscription
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Error occured with database transaction.",
        ) from e


@router.post("")
async def create_book_subscriptions(
    book_subscriptions: list[BookSubscriptionCreate], db: SDBDep, user: CurrentUser
) -> list[BookSubscription]:
    """Create a new book_subscription"""
    if not getattr(user, "email", None):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email is not found for user")

    subscriptions_created: list[BookSubscription] = []
    for book_subscription in book_subscriptions:
        # Ensure that the email is the same as the user's email
        book_subscription.email = user.email

        try:
            subscriptions_created.append(
                await book_subscription_crud.create(db, obj_in=book_subscription)
            )
        except Exception as e:
            print("Error occured with database transaction", e)

    return subscriptions_created


@router.put("/{id}")
async def update_book_subscription(
    id: str, book_subscription: BookSubscriptionUpdate, db: SDBDep, user: CurrentUser
) -> BookSubscription:
    """Update a book_subscription"""
    if not getattr(user, "email", None):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email is not found for user")
    try:
        return await book_subscription_crud.update(db, obj_in=book_subscription, i=id)
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Error occured with database transaction.",
        ) from e


@router.delete("/{id}")
async def delete_book_subscription(
    id: int, db: SDBDep, user: CurrentUser
) -> BookSubscription:
    """Delete a book_subscription"""
    if not getattr(user, "email", None):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email is not found for user")

    book_subscription = await book_subscription_crud.get(db, i=str(id))
    if book_subscription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book subscription not found",
        )
    if book_subscription.email != user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not allowed to delete this book subscription",
        )
    try:
        delete_book = await book_subscription_crud.delete(db, i=str(id))
        if delete_book is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book subscription not found",
            )
        return delete_book
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Error occured with database transaction.",
        ) from e
