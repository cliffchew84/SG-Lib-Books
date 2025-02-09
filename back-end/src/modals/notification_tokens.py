from datetime import datetime
from typing import ClassVar

from pydantic import BaseModel
from src.modals.base import ResponseBase, CreateBase, UpdateBase


class NotificationTokenBase(BaseModel):
    token: str
    email: str  # FK to user_subscription


class NotificationToken(ResponseBase, NotificationTokenBase):
    """Framework model for notification token response"""

    table_name: ClassVar[str] = "notification_tokens"
    pk: ClassVar[str] = "id"
    id: int
    created_at: datetime


class NotificationTokenCreate(CreateBase, NotificationTokenBase):
    """Framework model for creating new notification token"""


class NotificationTokenUpdateBase(BaseModel):
    token: str | None = None
    email: str | None = None


class NotificationTokenUpdate(UpdateBase, NotificationTokenUpdateBase):
    """Framework model for updating existing notification token"""
