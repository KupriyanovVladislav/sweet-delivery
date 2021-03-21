from time import strptime
from typing import List

from app.utils.constants import TIME_TEMPLATE


def validate_hours_periods(periods: List[str]) -> None:
    """If one of periods is invalid, it raise ValueError."""
    for period in periods:
        validate_period(period)


def validate_period(period: str) -> None:
    """If period is invalid, it raise ValueError."""
    period_times = period.split('-')
    if len(period_times) != 2:
        raise ValueError(
            f'Period {period} must contains 2 time points!',
        )
    try:
        for period_time in period_times:
            strptime(period_time, TIME_TEMPLATE)
    except ValueError:
        raise ValueError(f'Period {period} is invalid!')


def validate_regions(regions: List[int]) -> None:
    """If one of regions is invalid, it raise ValueError."""
    for region in regions:
        validate_region(region)


def validate_region(region: int) -> None:
    """If region is invalid, it raise ValueError."""
    if region <= 0 or not isinstance(region, int):
        raise ValueError(f'Region {region} is invalid')
