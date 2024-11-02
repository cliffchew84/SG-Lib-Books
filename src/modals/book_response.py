from collections import defaultdict
from functools import cached_property

from pydantic import BaseModel
from pydantic.fields import computed_field

from src.modals.book_avail import BookAvail
from src.modals.book_info import BookInfo


class BookResponse(BaseModel):
    book_avails: list[BookAvail]
    book_infos: list[BookInfo]
    library: str = "all"  # Cleaned library name (e.g. jurong west)

    @computed_field
    @cached_property
    def all_unique_books(self) -> list[BookInfo]:
        """Return list of book infos"""
        return self.book_infos

    @computed_field
    @cached_property
    def avail_bids(self) -> set[int]:
        """Return set of BID of books available"""
        return {
            book_avail.BID
            for book_avail in self.book_avails
            if book_avail.StatusDesc == "Available"
        }

    @computed_field
    @cached_property
    def lib_bids(self) -> set[int]:
        """Return set of BID of books in library"""
        return {
            book_avail.BID
            for book_avail in self.book_avails
            if (
                self.library == "all"  # Short-circuit to include all books
                or book_avail.BranchName.replace("Public", "")
                .replace("Library", "")
                .strip()
                .lower()
                == self.library
            )
        }

    @computed_field
    @cached_property
    def lib_item_nos(self) -> set[str]:
        """Return set of item nos of books in library"""
        return {
            book_avail.ItemNo
            for book_avail in self.book_avails
            if (
                self.library == "all"  # Short-circuit to include all books
                or book_avail.BranchName.replace("Public", "")
                .replace("Library", "")
                .strip()
                .lower()
                == self.library
            )
        }

    @computed_field
    @cached_property
    def all_avail_books(self) -> list[BookInfo]:
        """Return list of book infos if any book is available"""
        return [
            book_info
            for book_info in self.book_infos
            if book_info.BID in self.avail_bids
        ]

    @computed_field
    @cached_property
    def lib_all_books(self) -> list[BookInfo]:
        """Return list of book infos if book is in library"""
        return [
            book_info for book_info in self.book_infos if book_info.BID in self.lib_bids
        ]

    @computed_field
    @cached_property
    def lib_avail_books(self) -> list[BookInfo]:
        """Return list of book infos if book is in library and available"""
        return [
            book_info
            for book_info in self.book_infos
            if book_info.BID in self.lib_bids.intersection(self.avail_bids)
        ]

    @computed_field
    @cached_property
    def lib_book_summary(self) -> list[tuple[str, int]]:
        """Return list of tuple of cleaned library name and count of available books, sorted in ascending order"""
        book_counter: dict[str, int] = defaultdict(int)
        for book_avail in self.book_avails:
            branchName = (
                book_avail.BranchName.replace("Public", "")
                .replace("Library", "")
                .strip()
            )
            book_counter[branchName] += 1 if book_avail.BID in self.lib_bids else 0
        return sorted(book_counter.items())  # List of (lib_name: count)

    @computed_field
    @cached_property
    def api_data(self) -> list[dict]:
        """Return list of dict of book response api data that belongs to preferred library"""
        book_info_dict = {book_info.BID: book_info for book_info in self.book_infos}
        return [
            {**book_avail.model_dump(), **book_info_dict[book_avail.BID].model_dump()}
            for book_avail in self.book_avails
            if book_avail.ItemNo in self.lib_item_nos
        ]

    @computed_field
    @cached_property
    def book_infos_with_callnumber(self) -> list[dict]:
        """Return list of book info dictionary with callnumber"""
        callnumbers_by_bid = defaultdict(set)
        for avail in self.book_avails:
            callnumbers_by_bid[avail.BID].add(avail.CallNumber)
        return [
            # Get first callnumber from callnumber set if available
            {
                **book.model_dump(),
                "CallNumber": list(callnumbers_by_bid[book.BID])[0]
                if callnumbers_by_bid[book.BID]
                else "None",
            }
            for book in self.book_infos
        ]
