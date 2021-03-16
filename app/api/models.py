from pydantic import (
    BaseModel, Extra, Field, validator,
)
from typing import List, Optional

from app.utils.validators import validate_hours_periods, validate_regions
from app.db.schema import CourierTypeEnum


class Courier(BaseModel):
    id: int = Field(..., alias='courier_id')
    type: CourierTypeEnum = Field(..., alias='courier_type')
    regions: List[int]
    working_hours: List[str]

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


class CreateCourierRequest(BaseModel):
    data: List[Courier]


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
