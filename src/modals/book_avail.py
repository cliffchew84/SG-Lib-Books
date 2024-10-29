from datetime import date
from typing import ClassVar, Literal, Optional

from pydantic import BaseModel

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
    DueDate: Optional[date] = None


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
    DueDate: Optional[date] = None


class BookAvailUpdate(UpdateBase, BookAvailUpdateBase):
    """BookAvail model for updating existing book availability"""
