from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Union

from app.api.models import Courier, Order, OrderAssignTime
from app.db.managers import CouriersManager


class Interface(ABC):
    def __init__(self, courier_id: int, courier: Optional[Courier] = None):
        self.courier_id = courier_id
        self._db_courier = courier

    async def get_courier(self):
        if not self._db_courier:
            self._db_courier = await CouriersManager.get([self.courier_id], many=False)
        return self._db_courier


class IOrderAssigner(Interface):

    @abstractmethod
    def assign(self, orders: List[Order]) -> datetime:
        pass

    @abstractmethod
    def unassign(self, orders: List[Order]) -> None:
        pass

    @abstractmethod
    def complete(
        self, order: Union[int, Order], complete_time: datetime, duration: float,
    ) -> None:
        pass


class IOrderSelector(Interface):

    @abstractmethod
    def select(
        self,
        completed: bool = False,
        assign_time: Optional[datetime] = None,
        with_assign_time: bool = False,
    ) -> Union[List[OrderAssignTime], List[Order]]:
        pass

    @abstractmethod
    def select_suited_orders(self) -> List[Order]:
        pass


class IOrderFilter(Interface):

    @abstractmethod
    def filter_by_courier_features(self, orders: List[Order]) -> List[Order]:
        pass

    @abstractmethod
    def filter_by_region(self, orders: List[Order]) -> List[Order]:
        pass

    @abstractmethod
    def filter_by_time(self, orders: List[Order]) -> List[Order]:
        pass

    @abstractmethod
    def filter_by_weight(self, orders: List[Order]) -> List[Order]:
        pass
