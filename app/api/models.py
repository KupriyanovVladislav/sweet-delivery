from datetime import datetime
from typing import List, Optional

from pydantic import (
    BaseModel, Extra, Field, validator,
)

from app.db.schema import CourierTypeEnum
from app.utils.constants import MAX_WEIGHT, MIN_WEIGHT, RFC_TIME_FORMAT
from app.utils.validators import validate_hours_periods, validate_regions


class Courier(BaseModel):
    id: int = Field(..., alias='courier_id')
    type: CourierTypeEnum = Field(..., alias='courier_type')
    regions: List[int]
    working_hours: List[str]

    class Config:
        extra = Extra.forbid
        allow_population_by_field_name = True

    @validator('working_hours')
    def check_working_hours(cls, periods: List[str]):
        validate_hours_periods(periods)
        return periods

    @validator('regions')
    def check_regions(cls, regions: List[int]):
        validate_regions(regions)
        return regions


class CreateCourierRequest(BaseModel):
    data: List[Courier]


class CourierId(BaseModel):
    id: int


class CouriersPostRequest(BaseModel):
    couriers: List[CourierId]


class CourierPatchRequest(BaseModel):
    type: Optional[CourierTypeEnum] = Field(None, alias='courier_type')
    regions: Optional[List[int]] = None
    working_hours: Optional[List[str]] = None

    class Config:
        extra = Extra.forbid

    @validator('working_hours')
    def check_working_hours(cls, periods: List[str]):
        validate_hours_periods(periods)
        return periods

    @validator('regions')
    def check_regions(cls, regions: List[int]):
        validate_regions(regions)
        return regions


class Order(BaseModel):
    id: int = Field(..., alias='order_id')
    weight: float
    region: int
    delivery_hours: List[str]

    class Config:
        extra = Extra.forbid
        allow_population_by_field_name = True
        allow_mutation = False

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


class CreateOrdersRequest(BaseModel):
    data: List[Order]


class OrderId(BaseModel):
    id: int


class OrdersPostResponse(BaseModel):
    orders: List[OrderId]


class OrdersAssignPostRequest(BaseModel):
    courier_id: int


class OrdersAssignPostResponse(BaseModel):
    orders: List[OrderId] = []
    assign_time: Optional[str] = None


class OrderAssignTime(BaseModel):
    id: int = Field(..., alias='order_id')
    assign_time: datetime

    class Config:
        allow_population_by_field_name = True


class OrdersCompletePostRequest(BaseModel):
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
