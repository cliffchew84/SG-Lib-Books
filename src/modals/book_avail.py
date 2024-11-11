from datetime import datetime, timezone
from typing import ClassVar, Optional
from zoneinfo import ZoneInfo

from pydantic import BaseModel
from pydantic.fields import computed_field
from nlb_catalogue_client.models.item import Item

from src.modals.base import ResponseBase, CreateBase, UpdateBase

SingaporeTZ = ZoneInfo("Asia/Singapore")


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
            datetime.fromtimestamp(self.InsertTime, tz=timezone.utc)
            .astimezone(SingaporeTZ)
            .strftime("%d/%m %H:%M")
            if self.InsertTime
            else None
        )

    @computed_field
    @property
    def StatusDescWithDueDate(self) -> str:
        """Add Due Date to StatusDesc if available"""
        return (self.StatusDesc if self.StatusDesc else "Unknown") + (
            f" [{datetime.strptime(self.DueDate, '%Y-%m-%d').strftime('%d/%m')}]"
            if self.DueDate
            else ""
        )


class BookAvail(ResponseBase, BookAvailBase):
    table_name: ClassVar[str] = "books_avail"
    pk: ClassVar[str] = "ItemNo"


class BookAvailCreate(CreateBase, BookAvailBase):
    """BookAvail model for creating new book availability"""

    @staticmethod
    def from_nlb(book_item: Item) -> "BookAvailCreate":
        """Process book avail output from NLB API - GetAvailabilityInfo"""
        book_avail = BookAvailCreate(
            ItemNo=book_item.item_id if book_item.item_id else "",
            CallNumber=book_item.call_number if book_item.call_number else "Unknown",
            BranchName=book_item.location.name,
            StatusDesc=book_item.transaction_status.name,
            DueDate=None,
            InsertTime=int(datetime.now(tz=timezone.utc).timestamp()),
            BID=book_item.brn if book_item.brn else 0,
        )

        if book_avail.StatusDesc == "On Loan":
            book_avail.DueDate = (
                book_item.transaction_status.date.strftime("%Y-%m-%d")
                if book_item.transaction_status.date
                else None
            )

        return book_avail


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
