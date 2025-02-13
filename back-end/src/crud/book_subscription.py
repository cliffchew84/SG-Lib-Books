from typing import Optional

from supabase import Client

from src.crud.base import CRUDBase
from src.modals.book_subscription import (
    BookSubscription,
    BookSubscriptionCreate,
    BookSubscriptionUpdate,
)


class CRUDBookSubscription(
    CRUDBase[BookSubscription, BookSubscriptionCreate, BookSubscriptionUpdate]
):
    async def create(
        self,
        db: Client,
        *,
        obj_in: BookSubscriptionCreate,
        excludes: Optional[set[str]] = None,
    ) -> BookSubscription:
        return await super().create(db, obj_in=obj_in, excludes=excludes)

    async def get(self, db: Client, *, i: str) -> BookSubscription | None:
        return await super().get(db, i=i)

    async def get_all_by_bid(
        self, db: Client, bid: str, email: str
    ) -> list[BookSubscription]:
        response = (
            db.table(self.model.table_name)
            .select("*, books_avail!inner(BID)")
            .eq("email", email)
            .eq("books_avail.BID", bid)
            .execute()
        )
        return [self.model(**item) for item in response.data]

    async def get_all_by_item_nos(
        self, db: Client, itemNos: list[str]
    ) -> list[BookSubscription]:
        response = (
            db.table(self.model.table_name).select("*").in_("ItemNo", itemNos).execute()
        )
        return [self.model(**item) for item in response.data]

    async def get_all(self, db: Client) -> list[BookSubscription]:
        return await super().get_all(db)

    async def update(
        self,
        db: Client,
        *,
        obj_in: BookSubscriptionUpdate,
        i: str,
        excludes: Optional[set[str]] = None,
    ) -> BookSubscription:
        return await super().update(db, obj_in=obj_in, i=i, excludes=excludes)

    async def delete(self, db: Client, *, i: str) -> BookSubscription | None:
        return await super().delete(db, i=i)


book_subscription_crud = CRUDBookSubscription(BookSubscription)
