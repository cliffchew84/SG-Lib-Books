from supabase import Client

from src.crud.base import CRUDBase
from src.modals.book_info import (
    BookInfo,
    BookInfoCreate,
    BookInfoUpdate,
)
from src.modals.user_books import UserBook, UserBookCreate


class CRUDBookInfo(CRUDBase[BookInfo, BookInfoCreate, BookInfoUpdate]):
    async def create(self, db: Client, *, obj_in: BookInfoCreate) -> BookInfo:
        return await super().create(db, obj_in=obj_in)

    async def create_book_by_user(
        self, db: Client, obj_in: BookInfoCreate, username: str
    ) -> BookInfo:
        result = await super().create(db, obj_in=obj_in)

        # Add user book relationship table
        user_book = UserBookCreate(UserName=username, BID=obj_in.BID)
        db.table(UserBook.table_name).insert(user_book.model_dump()).execute()

        return result

    async def get(self, db: Client, *, i: str) -> BookInfo | None:
        return await super().get(db, i=i)

    async def get_all(self, db: Client) -> list[BookInfo]:
        return await super().get_all(db)

    async def get_multi_by_owner(self, db: Client, *, username: str) -> list[BookInfo]:
        response = (
            db.table(self.model.table_name)
            .select("*, user_books(UserName)")
            .eq("UserName", username)
            .execute()
        )
        return [self.model(**item) for item in response.data]

    async def update(self, db: Client, *, obj_in: BookInfoUpdate, i: str) -> BookInfo:
        return await super().update(db, obj_in=obj_in, i=i)

    async def delete(self, db: Client, *, i: str) -> BookInfo | None:
        return await super().delete(db, i=i)


book_info_crud = CRUDBookInfo(BookInfo)
