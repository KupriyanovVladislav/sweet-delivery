from typing import List, Union

from pydantic import BaseModel
from sqlalchemy import Table

from app.api.models import Courier, Order
from app.db import database
from app.db.schema import couriers_table, orders_table


class Manager:
    table: Table = Table
    model: BaseModel = BaseModel

    @classmethod
    async def create(cls, objects: List[BaseModel]) -> List[BaseModel]:
        query = cls.table.insert().values([
            obj.dict()
            for obj in objects
        ])
        await database.execute(query)
        return objects

    @classmethod
    async def get(
        cls,
        objects_ids: List[int],
        many: bool = True,
    ) -> Union[List[BaseModel], BaseModel, None]:
        query = cls.table.select().where(cls.table.c.id.in_(objects_ids))
        if many:
            return [cls.model(**obj) for obj in await database.fetch_all(query)]
        db_object = await database.fetch_one(query)
        return cls.model(**db_object) if db_object else None

    @classmethod
    async def update(cls, object_id: int, to_update: dict):
        to_update = {field: value for field, value in to_update.items() if value}
        if to_update:
            query = cls.table.update().where(
                cls.table.c.id == object_id,
            ).values(to_update)
            await database.execute(query)
        updated_object = await cls.get([object_id], many=False)
        return updated_object

    @classmethod
    async def delete(cls, objects_ids: List[int]):
        pass


class CouriersManager(Manager):
    table = couriers_table
    model = Courier


class OrdersManager(Manager):
    table = orders_table
    model = Order


def get_objects_ids(objects: Union[List[Courier], List[Order]]) -> List[int]:
    result = []
    try:
        result = [obj.id for obj in objects]
    except AttributeError:
        pass
    return result
