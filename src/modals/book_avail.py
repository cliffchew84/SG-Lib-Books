from datetime import datetime
from typing import ClassVar, Optional

import pendulum
from pydantic import BaseModel
from pydantic.fields import computed_field

from src.modals.base import ResponseBase, CreateBase, UpdateBase


class BookAvailBase(BaseModel):
    """Book Availability Info"""

    """Book Item number (PK)"""
    ItemNo: str

    """Book Call Number of Shelve"""
    CallNumber: str

    """Branch Name"""
    BranchName: str

    """Item loan status"""
    StatusDesc: Optional[str] = None

    """Database insert time (milliseconds after utc)"""
    InsertTime: Optional[int] = None

    """Book ID (FK)"""
    BID: int

    """Due Date"""
    DueDate: Optional[str] = None

    @computed_field
    @property
    def UpdateTime(self) -> str | None:
        """Compute insert time in desired format upon serialization"""
        return (
            datetime.fromtimestamp(
                self.InsertTime / 1e3, pendulum.timezone("Asia/Singapore")
            ).strftime("%d/%m %H:%M")
            if self.InsertTime
            else None
        )


class BookAvail(ResponseBase, BookAvailBase):
    table_name: ClassVar[str] = "books_avail"
    pk: ClassVar[str] = "ItemNo"


class BookAvailCreate(CreateBase, BookAvailBase):
    """BookAvail model for creating new book availability"""


class BookAvailUpdateBase(BaseModel):
    ItemNo: str
    CallNumber: Optional[str] = None
    BranchName: Optional[str] = None
    StatusDesc: Optional[str] = None
    InsertTime: Optional[int] = None
    BID: Optional[str] = None
    DueDate: Optional[str] = None


class BookAvailUpdate(UpdateBase, BookAvailUpdateBase):
    """BookAvail model for updating existing book availability"""
