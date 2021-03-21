from datetime import datetime, time
from typing import List, Optional, Tuple

from sqlalchemy import and_, select

from app.api.models import Courier, Order, OrderId, OrdersAssignPostResponse, OrderAssignTime
from app.db import database
from app.db.schema import couriers_orders_table, orders_table
from app.utils.constants import COURIER_POWER, TIME_TEMPLATE, RFC_TIME_FORMAT
from app.utils.exceptions import OrderForCourierNotExist
from app.utils.managers import CouriersManager


class OrdersAssigner:
    def __init__(self, courier_id, courier: Optional[Courier] = None):
        self.courier_id = courier_id
        self.db_courier = courier

    async def get_courier(self):
        if not self.db_courier:
            self.db_courier = await CouriersManager.get([self.courier_id], many=False)
        return self.db_courier

    async def get_current_orders(self):
        """Returns not completed orders for courier."""
        query = select([
            couriers_orders_table.c.order_id,
            couriers_orders_table.c.assign_time,
        ]).select_from(
            orders_table.join(couriers_orders_table),
        ).where(and_(
            couriers_orders_table.c.courier_id == self.courier_id,
            couriers_orders_table.c.complete_time == None,
        ))
        return [OrderAssignTime(**record) for record in await database.fetch_all(query)]

    async def get_suited_orders(self):
        courier = await self.get_courier()
        courier_power = COURIER_POWER.get(courier.type)
        query = select([
            orders_table.c.id,
            orders_table.c.region,
            orders_table.c.weight,
            orders_table.c.delivery_hours,
        ]).select_from(
            orders_table.join(couriers_orders_table, isouter=True),
        ).where(and_(
            couriers_orders_table.c.courier_id == None,
            orders_table.c.region.in_(courier.regions),
            orders_table.c.weight <= courier_power,
        ))
        orders = [Order(**order) for order in await database.fetch_all(query)]
        orders = self._get_suited_orders_by_time(orders, courier.working_hours)
        suited_orders = self._get_suited_orders_by_weight(orders, courier_power)
        return suited_orders

    def _get_suited_orders_by_time(
        self,
        orders: List[Order],
        working_hours: List[str],
    ) -> List[Order]:
        result = []
        for work_period in working_hours:
            work_start, work_end = self._convert_time_period(work_period)
            for order in orders:
                for delivery_period in order.delivery_hours:
                    delivery_start, delivery_end = self._convert_time_period(delivery_period)
                    if delivery_end >= work_start and delivery_start <= work_end:
                        order in result or result.append(order)  # It's funny :)
                        break
        return result

    @staticmethod
    def _get_suited_orders_by_weight(orders: List[Order], power: int) -> List[Order]:
        result = []
        current_weight = 0
        sorted_orders = sorted(orders, key=lambda obj: obj.weight)  # Because courier must have max amount of orders
        for order in sorted_orders:
            current_weight += order.weight
            if current_weight > power:
                break
            result.append(order)
        return result

    @staticmethod
    def _convert_time_period(time_period: str) -> Tuple[time, time]:
        return tuple(map(
            lambda time_str: datetime.strptime(time_str, TIME_TEMPLATE).time(),
            time_period.split('-'),
        ))

    async def assign_orders(self):
        orders = await self.get_current_orders()
        assign_time = None
        if orders:
            assign_time = orders[0].assign_time
        else:
            orders = await self.get_suited_orders()
            if orders:
                assign_time = datetime.now()
                query = couriers_orders_table.insert().values([
                    {'order_id': order.id, 'courier_id': self.courier_id, 'assign_time': assign_time}
                    for order in orders
                ])
                await database.execute(query)
        return OrdersAssignPostResponse(
            orders=[OrderId(id=order.id) for order in orders],
            assign_time=str(assign_time) if assign_time else None,
        )

    async def get_last_couriers_order(self):
        pass

    async def complete_order(self, order_id: int, complete_time: str):
        complete_time = datetime.strptime(complete_time, RFC_TIME_FORMAT)
        is_exists = await database.execute(
            couriers_orders_table.select().where(and_(
                couriers_orders_table.c.order_id == order_id,
                couriers_orders_table.c.courier_id == self.courier_id,
            )),
        )
        if not is_exists:
            raise OrderForCourierNotExist
        query = couriers_orders_table.update().where(and_(
            couriers_orders_table.c.order_id == order_id,
            couriers_orders_table.c.courier_id == self.courier_id,
        )).values(complete_time=complete_time)
        await database.execute(query)
