from datetime import datetime
from typing import ClassVar

from pydantic import BaseModel
from src.modals.base import ResponseBase, CreateBase, UpdateBase


class BookSubscriptionBase(BaseModel):
    ItemNo: str  # FK to book_avail
    email: str  # FK to user_subscription


class BookSubscription(ResponseBase, BookSubscriptionBase):
    """Framework model for book subscription response"""

    table_name: ClassVar[str] = "book_subscriptions"
    pk: ClassVar[str] = "id"
    id: int
    created_at: datetime


class BookSubscriptionCreate(CreateBase, BookSubscriptionBase):
    """Framework model for creating new book subscription"""


class BookSubscriptionUpdateBase(BaseModel):
    ItemNo: str | None = None
    email: str | None = None


class BookSubscriptionUpdate(UpdateBase, BookSubscriptionUpdateBase):
    """Framework model for updating existing book subscription"""
