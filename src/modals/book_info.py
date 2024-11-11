from typing import ClassVar, Optional

from pydantic import BaseModel

from src.modals.base import ResponseBase, CreateBase, UpdateBase


class BookInfoBase(BaseModel):
    """Book Info"""

    """Book Reference Number (BRN)"""

    BID: int

    """Book author"""
    TitleName: str

    """Book author"""
    Author: str

    """List of publish years"""
    PublishYear: str  # List[int]

    """List of publishers"""
    Publisher: str

    """List of subjects seperated by | """
    Subjects: str  # List[str]

    """List of isbns"""
    isbns: str  # List[int]


class BookInfo(ResponseBase, BookInfoBase):
    table_name: ClassVar[str] = "books_info"
    pk: ClassVar[str] = "BID"


class BookInfoCreate(CreateBase, BookInfoBase):
    """Framework model for creating new book_info"""


class BookInfoUpdateBase(BaseModel):
    BID: int
    TitleName: Optional[str] = None
    Author: Optional[str] = None
    PublishYear: Optional[str] = None
    Subjects: Optional[str] = None
    isbns: Optional[str] = None


class BookInfoUpdate(UpdateBase, BookInfoUpdateBase):
    """Framework model for updating existing book info"""
