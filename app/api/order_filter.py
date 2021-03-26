from datetime import datetime, time
from typing import List, Tuple

from app.api.models import Order
from app.api.interface import IOrderFilter
from app.utils.constants import TIME_TEMPLATE, COURIER_POWER


class OrderFilter(IOrderFilter):

    async def filter_by_courier_features(self, orders: List[Order]) -> List[Order]:
        orders = await self.filter_by_region(orders)
        orders = await self.filter_by_time(orders)
        return await self.filter_by_weight(orders)

    async def filter_by_region(self, orders: List[Order]) -> List[Order]:
        db_courier = await self.get_courier()
        return [
            order for order in orders
            if order.region in db_courier.regions
        ]

    async def filter_by_time(self, orders: List[Order]) -> List[Order]:
        """Returns orders which delivery hours intersect working hours."""
        result = []
        db_courier = await self.get_courier()
        for work_period in db_courier.working_hours:
            work_start, work_end = self._convert_time_period(work_period)
            for order in orders:
                for delivery_period in order.delivery_hours:
                    delivery_start, delivery_end = self._convert_time_period(delivery_period)
                    if delivery_end >= work_start and delivery_start <= work_end:  # Check segment intersecting
                        order in result or result.append(order)  # It's funny :)
                        break
        return result

    async def filter_by_weight(self, orders: List[Order]) -> List[Order]:
        """Returns list with max amount of orders."""
        result = []
        current_weight = 0
        db_courier = await self.get_courier()
        courier_power = COURIER_POWER.get(db_courier.type)
        for order in sorted(orders, key=lambda obj: obj.weight):  # Because courier must have max amount of orders
            current_weight += order.weight
            if current_weight > courier_power:
                break
            result.append(order)
        return result

    @staticmethod
    def _convert_time_period(time_period: str) -> Tuple[time, time]:
        """Convert string time period to tuple of time objects(start, end)."""
        return tuple(map(
            lambda time_str: datetime.strptime(time_str, TIME_TEMPLATE).time(),
            time_period.split('-'),
        ))


