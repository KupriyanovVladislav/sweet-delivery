from datetime import datetime
from typing import List, Union

from sqlalchemy import and_

from app.api.interface import IOrderAssigner
from app.api.models import Order
from app.db import database
from app.db.managers import get_objects_ids
from app.db.schema import couriers_orders_table
from app.utils.constants import COURIER_COEFFICIENT, RFC_TIME_FORMAT


class OrderAssigner(IOrderAssigner):

    async def assign(self, orders: List[Order]) -> datetime:
        assign_time = datetime.now()
        courier = await self.get_courier()
        coefficient = COURIER_COEFFICIENT.get(courier.type)
        query = couriers_orders_table.insert().values([
            {
                'order_id': order.id, 'courier_id': self.courier_id,
                'assign_time': assign_time, 'coefficient': coefficient,
            }
            for order in orders
        ])
        await database.execute(query)
        return assign_time

    async def unassign(self, orders: List[Order]) -> None:
        orders_ids = get_objects_ids(orders)
        query = couriers_orders_table.delete().where(and_(
            couriers_orders_table.c.order_id.in_(orders_ids),
            couriers_orders_table.c.courier_id == self.courier_id,
        ))
        await database.execute(query)

    async def complete(
        self, order: Union[int, Order], complete_time: datetime, duration: float,
    ) -> None:
        if not isinstance(order, int):
            order = order.id

        query = couriers_orders_table.update().where(and_(
            couriers_orders_table.c.order_id == order,
            couriers_orders_table.c.courier_id == self.courier_id,
        )).values(
            complete_time=complete_time,
            duration=duration,
        )

        await database.execute(query)
