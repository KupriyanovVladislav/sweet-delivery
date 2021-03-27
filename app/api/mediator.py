from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import and_

from app.api.exceptions import (InvalidCompleteTime, OrderAlreadyCompleted,
                                OrderForCourierNotExist)
from app.api.interface import Interface
from app.api.models import Courier, Order
from app.api.order_assigner import OrderAssigner
from app.api.order_filter import OrderFilter
from app.api.order_selector import OrderSelector
from app.db import database
from app.db.managers import get_objects_ids
from app.db.schema import couriers_orders_table
from app.utils.constants import RFC_TIME_FORMAT


class OrderAssignMediator(Interface):
    """Class which unions work of order assigner, selector and filter."""

    async def assign(self) -> Tuple[List[Order], Optional[str]]:
        """
        Assign logic:
        1. Get not completed orders.
        2. If (1) exist then return they.
        3. If (1) not exist then try find suited orders.
        4. If (3) not exist return empty (orders=[], assign_time=null).
        """
        db_courier = await self.get_courier()
        order_selector = OrderSelector(courier_id=self.courier_id, courier=db_courier)

        orders = await order_selector.select(completed=False, with_assign_time=True)  # Get not completed orders
        assign_time = None
        if orders:
            assign_time = orders[0].assign_time  # Last assign time

        else:  # If not completed orders does not exist then we must found suited orders
            orders = await order_selector.select_suited_orders()  # Orders which is not belong to other couriers
            if orders:
                order_filter = OrderFilter(courier_id=self.courier_id, courier=db_courier)
                orders = await order_filter.filter_by_courier_features(orders)
                if orders:  # If we don't find suited return orders=[], assign_time=null
                    order_assigner = OrderAssigner(courier_id=self.courier_id, courier=db_courier)
                    assign_time = await order_assigner.assign(orders)

        assign_time = assign_time.strftime(RFC_TIME_FORMAT) if assign_time else None
        return orders, assign_time

    async def unassign(self) -> None:
        """Unassign orders if they exist."""
        db_courier = await self.get_courier()

        order_assigner = OrderAssigner(courier_id=self.courier_id, courier=db_courier)
        order_selector = OrderSelector(courier_id=self.courier_id, courier=db_courier)
        order_filter = OrderFilter(courier_id=self.courier_id, courier=db_courier)

        current_orders = await order_selector.select(completed=False)
        suited_orders = await order_filter.filter_by_courier_features(current_orders)

        if len(current_orders) != len(suited_orders):
            orders_ids_to_unassign = set(get_objects_ids(current_orders)) - set(get_objects_ids(suited_orders))
            orders_to_unassign = [order for order in current_orders if order.id in orders_ids_to_unassign]
            await order_assigner.unassign(orders_to_unassign)

    async def complete(self, order_id: int, complete_time: str):
        """Mark order completed with computing duration."""
        entry = await database.fetch_one(
            couriers_orders_table.select().where(and_(
                couriers_orders_table.c.order_id == order_id,
                couriers_orders_table.c.courier_id == self.courier_id,
            )),
        )
        if not entry:
            raise OrderForCourierNotExist
        elif entry.get('complete_time') is not None:
            raise OrderAlreadyCompleted

        db_courier = await self.get_courier()
        order_assigner = OrderAssigner(courier_id=self.courier_id, courier=db_courier)
        complete_time = datetime.strptime(complete_time, RFC_TIME_FORMAT)
        assign_time = entry.get('assign_time')  # Assign time of this order
        # Get date of last completed order from current delivery
        last_order_complete_time = await self._get_last_order_date(assign_time)
        # assign time will be None if courier doesn't have completed orders.
        if not last_order_complete_time:
            last_order_complete_time = assign_time
        duration = self._find_duration(last_order_complete_time, complete_time)

        await order_assigner.complete(order_id, complete_time, duration)

    @staticmethod
    def _find_duration(start_date, end_date) -> float:
        diff = (end_date - start_date).total_seconds()
        if diff < 0:
            raise InvalidCompleteTime
        return diff

    async def _get_last_order_date(self, assign_time: datetime) -> Optional[datetime]:
        """Returns date of last completed order from current delivery."""
        db_courier = await self.get_courier()
        order_selector = OrderSelector(courier_id=self.courier_id, courier=db_courier)
        orders = await order_selector.select(
            completed=True,
            assign_time=assign_time,
            with_assign_time=True,
        )  # Get sorted completed orders from current delivery
        return orders[-1].complete_time if orders else None
