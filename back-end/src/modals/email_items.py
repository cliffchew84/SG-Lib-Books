from datetime import datetime
from typing import ClassVar

from pydantic import BaseModel

from src.modals.base import ResponseBase, CreateBase, UpdateBase


class EmailItemsBase(BaseModel):
    """Email items Table"""

    BID: int

    """Book title"""
    TitleName: str | None

    """Book author"""
    Author: str | None

    """Cover photo url"""
    cover_url: str | None

    """URL to book details"""
    url: str | None

    """Branch with recently available book"""
    BranchName: list[str]

    """FK to user"""
    email: str


class EmailItems(ResponseBase, EmailItemsBase):
    table_name: ClassVar[str] = "email_items"
    id: int  # Auto incremented by database
    created_at: datetime  # Auto populated by database


class EmailItemsCreate(CreateBase, EmailItemsBase):
    """Notification model for creating new user-notification relationship"""


class EmailItemsUpdateBase(BaseModel):
    BID: int | None = None
    TitleName: str | None = None
    Author: str | None = None
    cover_url: str | None = None
    url: str | None = None
    BranchName: list[str] | None = None
    email: str | None = None


class EmailItemsUpdate(UpdateBase, EmailItemsUpdateBase):
    """EmailItems model for updating emailItems"""
