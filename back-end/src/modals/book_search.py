from pydantic import BaseModel

from src.modals.book_info import BookInfo


class SearchResponse(BaseModel):
    total_records: int
    has_more_records: bool
    next_offset: int
    titles: list[BookInfo]
