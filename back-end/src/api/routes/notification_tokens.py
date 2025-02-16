from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, status, HTTPException

from src.api.deps import SDBDep, CurrentUser
from src.crud.notification_tokens import notification_token_crud
from src.modals.notification_tokens import NotificationTokenCreate, NotificationToken

router = APIRouter()


@router.post("/{token}")
async def register_token(
    token: str,
    db: SDBDep,
    user: CurrentUser,
) -> NotificationToken:
    """Register a new notification token, checking for duplicates."""
    if not user or not user.email:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email is not found for user")

    try:
        existing_token = await notification_token_crud.get_by_token(db, token=token)
        if existing_token:
            return existing_token

        new_token = await notification_token_crud.create(
            db, obj_in=NotificationTokenCreate(token=token, email=user.email)
        )
        return new_token

    except Exception as e:
        print(e)
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Error occurred with database transaction.",
        ) from e


@router.delete("/cleanup", status_code=status.HTTP_204_NO_CONTENT)
async def cleanup_old_tokens(
    db: SDBDep,
    user: CurrentUser,
) -> None:
    """Remove notification tokens older than 30 days."""
    if not user or not user.email:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email is not found for user")

    try:
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        old_tokens = await notification_token_crud.get_older_than(
            db, date=thirty_days_ago
        )
        for token in old_tokens:
            await notification_token_crud.delete(db, i=str(token.id))

    except Exception as e:
        print(e)
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Error occurred with database transaction.",
        ) from e


@router.delete("/{token}", status_code=status.HTTP_204_NO_CONTENT)
async def deregister_token(
    token: str,
    db: SDBDep,
    user: CurrentUser,
) -> None:
    """Deregister a notification token based on the given token."""
    if not user or not user.email:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email is not found for user")

    try:
        existing_token = await notification_token_crud.get_by_token(db, token=token)
        if not existing_token:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                f"Token {token} could not be found in the database.",
            )

        await notification_token_crud.delete(db, i=str(existing_token.id))

    except Exception as e:
        print(e)
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Error occurred with database transaction.",
        ) from e
