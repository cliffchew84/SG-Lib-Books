from typing import Optional

from supabase import Client

from src.crud.base import CRUDBase
from src.modals.email_items import (
    EmailItems,
    EmailItemsCreate,
    EmailItemsUpdate,
)


class CRUDEmailItems(
    CRUDBase[
        EmailItems,
        EmailItemsCreate,
        EmailItemsUpdate,
    ]
):
    async def create(
        self,
        db: Client,
        *,
        obj_in: EmailItemsCreate,
        excludes: Optional[set[str]] = None,
    ) -> EmailItems:
        return await super().create(db, obj_in=obj_in, excludes=excludes)

    async def get(self, db: Client, *, i: str) -> EmailItems | None:
        return await super().get(db, i=str(i))

    async def get_all(self, db: Client) -> list[EmailItems]:
        return await super().get_all(db)

    async def get_by_email(self, db: Client, *, email: str) -> list[EmailItems]:
        response = (
            db.table(self.model.table_name).select("*").eq("email", email).execute()
        )
        return [EmailItems(**item) for item in response.data]

    async def update(
        self,
        db: Client,
        *,
        obj_in: EmailItemsUpdate,
        i: str,
        excludes: Optional[set[str]] = None,
    ) -> EmailItems:
        return await super().update(db, obj_in=obj_in, i=i, excludes=excludes)

    async def delete(self, db: Client, *, i: str) -> EmailItems | None:
        return await super().delete(db, i=str(i))


email_items_crud = CRUDEmailItems(EmailItems)
