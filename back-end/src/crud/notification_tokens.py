from typing import Optional
from datetime import datetime

from supabase import Client

from src.crud.base import CRUDBase
from src.modals.notification_tokens import (
    NotificationToken,
    NotificationTokenCreate,
    NotificationTokenUpdate,
)


class CRUDNotificationToken(
    CRUDBase[
        NotificationToken,
        NotificationTokenCreate,
        NotificationTokenUpdate,
    ]
):
    async def create(
        self,
        db: Client,
        *,
        obj_in: NotificationTokenCreate,
        excludes: Optional[set[str]] = None,
    ) -> NotificationToken:
        return await super().create(db, obj_in=obj_in, excludes=excludes)

    async def get(self, db: Client, *, i: str) -> NotificationToken | None:
        return await super().get(db, i=i)

    async def get_by_token(self, db: Client, token: str) -> NotificationToken | None:
        response = (
            db.table(self.model.table_name).select("*").eq("token", token).execute()
        )
        return NotificationToken(**response.data[0]) if response.data else None

    async def get_older_than(
        self, db: Client, *, date: datetime
    ) -> list[NotificationToken]:
        response = (
            db.table(self.model.table_name)
            .select("*")
            .lt("created_at", date.isoformat())
            .execute()
        )
        return [self.model(**item) for item in response.data]

    async def get_all(self, db: Client) -> list[NotificationToken]:
        return await super().get_all(db)

    async def update(
        self,
        db: Client,
        *,
        obj_in: NotificationTokenUpdate,
        i: str,
        excludes: Optional[set[str]] = None,
    ) -> NotificationToken:
        return await super().update(db, obj_in=obj_in, i=i, excludes=excludes)

    async def delete(self, db: Client, *, i: str) -> NotificationToken | None:
        return await super().delete(db, i=i)


notification_token_crud = CRUDNotificationToken(NotificationToken)
