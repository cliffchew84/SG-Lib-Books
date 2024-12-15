from datetime import datetime
from typing import ClassVar

from pydantic import BaseModel

from src.modals.base import ResponseBase, CreateBase, UpdateBase


class BookOutdatedBIDBase(BaseModel):
    """Book Info"""

    """Book Reference Number (BRN)"""
    BID: int

    """last_updated time"""
    last_updated: datetime


class BookOutdatedBID(ResponseBase, BookOutdatedBIDBase):
    table_name: ClassVar[str] = "outdated_bid_datetime"
    pk: ClassVar[str] = "BID"


class BookOutdatedBIDCreate(CreateBase, BookOutdatedBIDBase):
    """Framework model for creating new book_outdated"""


class BookOutdatedBIDUpdate(UpdateBase):
    """Framework model for updating existing book_outdated"""
