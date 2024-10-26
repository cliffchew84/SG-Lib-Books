from typing import Generic, TypeVar

from supabase import Client

from src.modals.base import CreateBase, ResponseBase, UpdateBase

ModelT = TypeVar("ModelT", bound=ResponseBase)
CreateSchemaT = TypeVar("CreateSchemaT", bound=CreateBase)
UpdateSchemaT = TypeVar("UpdateSchemaT", bound=UpdateBase)


class CRUDBase(Generic[ModelT, CreateSchemaT, UpdateSchemaT]):
    """Basic CRUD operations"""

    def __init__(self, model: type[ModelT]):
        self.model = model

    async def get(self, db: Client, *, i: str) -> ModelT | None:
        """get by table_name by id"""
        response = (
            db.table(self.model.table_name).select("*").eq(self.model.pk, i).execute()
        )
        got = response.data
        return self.model(**got[0]) if got else None

    async def get_all(self, db: Client) -> list[ModelT]:
        """get all by table_name"""
        response = db.table(self.model.table_name).select("*").execute()
        return [self.model(**item) for item in response.data]

    async def get_multi_by_owner(self, db: Client, *, username: str) -> list[ModelT]:
        """get by owner,use it  if rls failed to use"""
        response = (
            db.table(self.model.table_name)
            .select("*")
            .eq("UserName", username)
            .execute()
        )
        return [self.model(**item) for item in response.data]

    async def create(
        self,
        db: Client,
        *,
        obj_in: CreateSchemaT,
    ) -> ModelT:
        """create by CreateSchemaT"""
        response = db.table(self.model.table_name).insert(obj_in.model_dump()).execute()

        return self.model(**response.data[0])

    async def update(self, db: Client, *, obj_in: UpdateSchemaT, i: str) -> ModelT:
        """update by UpdateSchemaT"""
        data, _ = (
            db.table(self.model.table_name)
            .update(obj_in.model_dump(exclude_unset=True))
            .eq(self.model.pk, i)
            .execute()
        )
        _, updated = data
        return self.model(**updated[0])

    async def delete(self, db: Client, *, i: str) -> ModelT | None:
        """remove by UpdateSchemaT"""
        data, _ = (
            db.table(self.model.table_name).delete().eq(self.model.pk, i).execute()
        )
        _, deleted = data
        if not deleted:
            return None
        return self.model(**deleted[0])
