from datetime import date
from typing import ClassVar, Literal, Optional

from pydantic import BaseModel

from src.modals.base import ResponseBase, CreateBase, UpdateBase

StatusDescName = Literal[
    # List of item status name from (C003):
    # https://openweb.nlb.gov.sg/api/References/Catalogue.html
    "In-Process",
    "In-Transit",
    "Shelving",
    "On Shelf",
    "Reservation In-Transit",
    "On-Hold",
    "On-Loan",
    "Claim Missing Parts",
    "Claim Never Borrowed",
    "Claim Returned",
    "Lost",
    "Missing",
    "At binding",
    "Unavailable",
    "Weeding",
]


class BookAvailBase(BaseModel):
    """Book Availability Info"""

    """Book Item number (PK)"""
    ItemNo: str

    """Book Call Number of Shelve"""
    CallNumber: str

    """Branch Name"""
    BranchName: str

    """Item loan status"""
    StatusDesc: StatusDescName

    """Database insert time (milliseconds after utc)"""
    InsertTime: int

    """Book ID (FK)"""
    BID: int

    """Due Date"""
    DueDate: date


class BookAvail(ResponseBase, BookAvailBase):
    table_name: ClassVar[str] = "books_avail"


class BookAvailCreate(CreateBase, BookAvailBase):
    """BookAvail model for creating new book availability"""


class BookAvailUpdateBase(BaseModel):
    ItemNo: str
    CallNumber: Optional[str] = None
    BranchName: Optional[str] = None
    StatusDesc: Optional[StatusDescName] = None
    InsertTime: Optional[int] = None
    BID: Optional[str] = None
    DueDate: Optional[date] = None


class BookInfoUpdate(UpdateBase, BookAvailUpdateBase):
    """BookAvail model for updating existing book availability"""
