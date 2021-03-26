from typing import List, Optional

from sqlalchemy import and_, func, select

from app.api.models import Courier
from app.db import database
from app.db.schema import orders_table, couriers_orders_table


class CourierStatistic:
    def __init__(self, courier: Courier):
        self.courier = courier

    async def get_rating(self) -> float:
        min_avg_duration = await self._find_min_avg_duration()
        return self._compute_rating(min_avg_duration) if min_avg_duration else 0

    async def get_earnings(self) -> int:
        columns = (couriers_orders_table.c.coefficient,)
        query = self._get_query(columns)
        select_result = await database.fetch_all(query)
        coeffs = [row.get('coefficient') for row in select_result]
        return self._compute_earnings(coeffs)

    async def _find_min_avg_duration(self) -> Optional[float]:
        """Find min average time group by regions."""
        column_name = 'average_time'
        columns = (func.avg(couriers_orders_table.c.duration).label(column_name),)
        query = self._get_query(columns).group_by(orders_table.c.region).limit(1)
        select_result = await database.fetch_one(query)
        return select_result.get(column_name) if select_result else None

    @staticmethod
    def _compute_rating(t: float) -> float:
        rating = (1 - min(t, 60*60)/(60*60)) * 5
        return round(rating, 2)

    @staticmethod
    def _compute_earnings(coeffs: List[int]) -> int:
        return 500 * sum(coeffs)

    def _get_query(self, columns):
        return select(columns).select_from(
            orders_table.join(couriers_orders_table),
        ).where(and_(
            couriers_orders_table.c.courier_id == self.courier.id,
            couriers_orders_table.c.complete_time.isnot(None),
        ))
