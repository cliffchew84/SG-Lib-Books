from src.modals.book_avail import BookAvail
from src.modals.book_info import BookInfo


class BookResponse(BookInfo):
    avails: list[BookAvail]
