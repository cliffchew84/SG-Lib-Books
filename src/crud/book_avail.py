from supabase import Client

from src.crud.base import CRUDBase
from src.modals.book_avail import (
    BookAvail,
    BookAvailCreate,
    BookAvailUpdate,
)


class CRUDBookAvail(CRUDBase[BookAvail, BookAvailCreate, BookAvailUpdate]):
    async def create(self, db: Client, *, obj_in: BookAvailCreate) -> BookAvail:
        return await super().create(db, obj_in=obj_in)

    async def get(self, db: Client, *, i: str) -> BookAvail | None:
        return await super().get(db, i=i)

    async def get_all(self, db: Client) -> list[BookAvail]:
        return await super().get_all(db)

    async def get_multi_by_owner(self, db: Client, *, username: str) -> list[BookAvail]:
        response = (
            db.table(self.model.table_name)
            .select("*, user_books(UserName)")
            .eq("UserName", username)
            .execute()
        )
        return [self.model(**item) for item in response.data]

    async def update(self, db: Client, *, obj_in: BookAvailUpdate, i: str) -> BookAvail:
        return await super().update(db, obj_in=obj_in, i=i)

    async def delete(self, db: Client, *, i: str) -> BookAvail | None:
        return await super().delete(db, i=i)


book_avail_crud = CRUDBookAvail(BookAvail)
