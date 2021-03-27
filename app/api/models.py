from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Extra, Field, validator

from app.db.schema import CourierTypeEnum
from app.utils.constants import MAX_WEIGHT, MIN_WEIGHT, RFC_TIME_FORMAT
from app.utils.validators import validate_hours_periods, validate_regions


class Base(BaseModel):
    class Config:
        extra = Extra.forbid
        allow_population_by_field_name = True


class Courier(Base):
    id: int = Field(..., alias='courier_id')
    type: CourierTypeEnum = Field(..., alias='courier_type')
    regions: List[int]
    working_hours: List[str]

    @validator('working_hours')
    def check_working_hours(cls, periods: List[str]):
        validate_hours_periods(periods)
        return periods

    @validator('regions')
    def check_regions(cls, regions: List[int]):
        validate_regions(regions)
        return regions


class CouriersPostRequest(Base):
    data: List[Courier]


class CourierId(Base):
    id: int


class CouriersPostResponse(Base):
    couriers: List[CourierId]


class CourierPatchRequest(Base):
    type: Optional[CourierTypeEnum] = Field(None, alias='courier_type')
    regions: Optional[List[int]] = None
    working_hours: Optional[List[str]] = None

    @validator('working_hours')
    def check_working_hours(cls, periods: List[str]):
        validate_hours_periods(periods)
        return periods

    @validator('regions')
    def check_regions(cls, regions: List[int]):
        validate_regions(regions)
        return regions


class Order(Base):
    id: int = Field(..., alias='order_id')
    weight: float
    region: int
    delivery_hours: List[str]

    @validator('weight')
    def check_positive_weight(cls, weight):
        if not MIN_WEIGHT <= weight <= MAX_WEIGHT:
            raise ValueError('Weight must be positive!')
        return weight

    @validator('region')
    def check_region(cls, region):
        if region <= 0:
            raise ValueError('Region is invalid!')
        return region

    @validator('delivery_hours')
    def check_delivery_hours(cls, periods: List[str]):
        validate_hours_periods(periods)
        return periods


class OrdersPostRequest(Base):
    data: List[Order]


class OrderId(Base):
    id: int


class OrdersPostResponse(Base):
    orders: List[OrderId]


class OrdersAssignPostRequest(Base):
    courier_id: int

    class Config:
        extra = Extra.forbid


class OrdersAssignPostResponse(Base):
    orders: List[OrderId] = []
    assign_time: Optional[str] = None


class OrderAssignTime(Base):
    id: int = Field(..., alias='order_id')
    assign_time: datetime
    complete_time: Optional[datetime] = None


class OrdersCompletePostRequest(Base):
    courier_id: int
    order_id: int
    complete_time: str

    @validator('complete_time')
    def check_complete_time(cls, value: str):
        try:
            datetime.strptime(value, RFC_TIME_FORMAT)
        except ValueError:
            raise ValueError('Complete time is invalid!')
        return value


class CourierGetResponse(Courier):
    rating: Optional[float]
    earnings: int
