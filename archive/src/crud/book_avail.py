from typing import Optional

from supabase import Client

from src.crud.base import CRUDBase
from src.crud.book_info import book_info_crud
from src.modals.book_avail import (
    BookAvail,
    BookAvailCreate,
    BookAvailUpdate,
)


class CRUDBookAvail(CRUDBase[BookAvail, BookAvailCreate, BookAvailUpdate]):
    async def create(
        self,
        db: Client,
        *,
        obj_in: BookAvailCreate,
        excludes: Optional[set[str]] = {"UpdateTime", "StatusDescWithDueDate"},
    ) -> BookAvail:
        return await super().create(db, obj_in=obj_in, excludes=excludes)

    async def get(self, db: Client, *, i: str) -> BookAvail | None:
        return await super().get(db, i=i)

    async def get_all(self, db: Client) -> list[BookAvail]:
        return await super().get_all(db)

    async def get_multi_by_owner(
        self, db: Client, *, username: str, BIDs: Optional[list[int]] = None
    ) -> list[BookAvail]:
        if BIDs is None:
            book_infos = await book_info_crud.get_multi_by_owner(db, username=username)
            BIDs = [book_info.BID for book_info in book_infos]
        response = (
            db.table(self.model.table_name).select("*").in_("BID", BIDs).execute()
        )
        return [BookAvail(**item) for item in response.data]

    async def update(
        self,
        db: Client,
        *,
        obj_in: BookAvailUpdate,
        i: str,
        excludes: Optional[set[str]] = {"UpdateTime", "StatusDescWithDueDate"},
    ) -> BookAvail:
        return await super().update(db, obj_in=obj_in, i=i, excludes=excludes)

    async def upsert(
        self,
        db: Client,
        *,
        obj_ins: list[BookAvailCreate],
        excludes: Optional[set[str]] = {"UpdateTime", "StatusDescWithDueDate"},
    ) -> list[BookAvail]:
        return await super().upsert(db, obj_ins=obj_ins, excludes=excludes)

    async def delete(self, db: Client, *, i: str) -> BookAvail | None:
        return await super().delete(db, i=i)


book_avail_crud = CRUDBookAvail(BookAvail)
