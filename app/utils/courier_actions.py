from typing import List
from app.db import database
from app.db.schema import couriers_table
from app.api.models import Courier


async def get_couriers_by_ids(courier_ids: List[int], many: bool = True):
    query = couriers_table.select().where(couriers_table.c.id.in_(courier_ids))
    if many:
        return await database.fetch_all(query)
    return await database.fetch_one(query)


async def create_couriers(couriers: List[Courier]):
    query = couriers_table.insert().values([
        courier.dict()
        for courier in couriers
    ])
    await database.execute(query)


async def update_courier(courier_id: int, to_update: dict):
    to_update = {field: value for field, value in to_update.items() if value}
    if to_update:
        query = couriers_table.update().where(
            couriers_table.c.id == courier_id,
        ).values(to_update)
        await database.execute(query)


def get_couriers_ids(couriers: List[Courier]):
    return [courier.id for courier in couriers]


# class PostCourierResponse:
#     def __call__(self, couriers: List[Courier], success=True):
#         result = {'couriers': []}
#         for courier_id in get_couriers_ids(couriers):
#             result['couriers'].append({'id': courier_id})
#         return result


def post_courier_response(couriers: List[Courier]):
    result = {'couriers': []}
    for courier_id in get_couriers_ids(couriers):
        result['couriers'].append({'id': courier_id})
    return result
