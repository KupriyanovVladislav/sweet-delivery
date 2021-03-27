from typing import List, Union

from sqlalchemy import and_, select

from app.api.interface import IOrderSelector
from app.api.models import Order, OrderAssignTime
from app.db import database
from app.db.schema import couriers_orders_table, orders_table


class OrderSelector(IOrderSelector):

    async def select(
        self,
        completed: bool = False,
        with_assign_time: bool = False,
    ) -> Union[List[OrderAssignTime], List[Order]]:
        """Returns sorted (not) completed orders for courier."""
        where_conditions = [couriers_orders_table.c.courier_id == self.courier_id]
        order_columns = [couriers_orders_table.c.assign_time]
        if not completed:
            where_conditions.append(couriers_orders_table.c.complete_time.is_(None))
        else:
            where_conditions.append(couriers_orders_table.c.complete_time.isnot(None))
            order_columns.append(couriers_orders_table.c.complete_time)

        model = Order
        columns = [
            orders_table.c.id,
            orders_table.c.region,
            orders_table.c.weight,
            orders_table.c.delivery_hours,
        ]
        if with_assign_time:
            model = OrderAssignTime
            columns = [
                couriers_orders_table.c.order_id,
                couriers_orders_table.c.assign_time,
                couriers_orders_table.c.complete_time,
            ]

        query = select(columns).select_from(
            orders_table.join(couriers_orders_table),
        ).where(and_(
            *where_conditions,
        )).order_by(
            couriers_orders_table.c.complete_time,
            couriers_orders_table.c.assign_time,
        )
        return [model(**record) for record in await database.fetch_all(query)]

    async def select_suited_orders(self) -> List[Order]:
        query = select([
            orders_table.c.id,
            orders_table.c.region,
            orders_table.c.weight,
            orders_table.c.delivery_hours,
        ]).select_from(
            orders_table.join(couriers_orders_table, isouter=True),
        ).where(and_(
            couriers_orders_table.c.courier_id.is_(None),  # Orders of one courier not must be available for other
        ))
        orders = [Order(**order) for order in await database.fetch_all(query)]
        return orders
