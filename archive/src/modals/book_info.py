from typing import ClassVar, Optional

from pydantic import BaseModel
from nlb_catalogue_client.models.get_title_details_response_v2 import (
    GetTitleDetailsResponseV2,
)

from src.modals.base import ResponseBase, CreateBase, UpdateBase


class BookInfoBase(BaseModel):
    """Book Info"""

    """Book Reference Number (BRN)"""

    BID: int

    """Book author"""
    TitleName: str | None

    """Book author"""
    Author: str | None

    """List of publish years"""
    PublishYear: str | None  # List[int]

    """List of publishers"""
    Publisher: str | None

    """List of subjects seperated by | """
    Subjects: str | None  # List[str]

    """List of isbns"""
    isbns: str | None  # List[int]


class BookInfo(ResponseBase, BookInfoBase):
    table_name: ClassVar[str] = "books_info"
    pk: ClassVar[str] = "BID"


class BookInfoCreate(CreateBase, BookInfoBase):
    """Framework model for creating new book_info"""

    @staticmethod
    def from_nlb(item: GetTitleDetailsResponseV2) -> "BookInfoCreate":
        """Process book info output from NLB API - GetTitleDetails"""
        subjects = " | ".join(
            {subject.replace(".", "") for subject in item.subjects or []}
        )
        book_info = BookInfoCreate(
            BID=item.brn if item.brn else 0,
            TitleName=item.title if item.title else None,
            Author=item.author if item.author else None,
            PublishYear=item.publish_date if item.publish_date else None,
            Subjects=subjects if subjects else None,
            Publisher=str(item.publisher) if item.publisher else None,
            isbns=str(item.isbns) if item.isbns else None,
        )

        return book_info


class BookInfoUpdateBase(BaseModel):
    BID: int
    TitleName: Optional[str] = None
    Author: Optional[str] = None
    PublishYear: Optional[str] = None
    Subjects: Optional[str] = None
    isbns: Optional[str] = None


class BookInfoUpdate(UpdateBase, BookInfoUpdateBase):
    """Framework model for updating existing book info"""
