from typing import Optional

from supabase import Client

from src.crud.base import CRUDBase
from src.modals.book_outdated_bid import (
    BookOutdatedBID,
    BookOutdatedBIDCreate,
    BookOutdatedBIDUpdate,
)


class CRUDBookOutdatedBID(
    CRUDBase[
        BookOutdatedBID,
        BookOutdatedBIDCreate,
        BookOutdatedBIDUpdate,
    ]
):
    async def create(
        self,
        db: Client,
        *,
        obj_in: BookOutdatedBIDCreate,
        excludes: Optional[set[str]] = None,
    ) -> BookOutdatedBID:
        raise NotImplementedError("View table is read only")

    async def get(self, db: Client, *, i: str) -> BookOutdatedBID | None:
        return await super().get(db, i=i)

    async def get_all(self, db: Client) -> list[BookOutdatedBID]:
        return await super().get_all(db)

    async def update(
        self,
        db: Client,
        *,
        obj_in: BookOutdatedBIDUpdate,
        i: str,
        excludes: Optional[set[str]] = None,
    ) -> BookOutdatedBID:
        raise NotImplementedError("View table is read only")

    async def delete(self, db: Client, *, i: str) -> BookOutdatedBID | None:
        raise NotImplementedError("View table is read only")


book_outdated_bid_crud = CRUDBookOutdatedBID(BookOutdatedBID)
