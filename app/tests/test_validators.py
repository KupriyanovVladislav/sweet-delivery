import pytest

from app.utils.validators import validate_hours_periods


def test_validate_hours_periods():
    invalid_periods = [
        ['12:30 14:00'],  # Without '-'
        ['12.30-14.00'],  # Invalid time format. Must be 'HH:MM'
        ['12:30-14:00', '15:00 17:00'],  # One period is invalid
        ['12:30-14:00-17:00'],  # Period must contain just 2 point
    ]
    for period in invalid_periods:
        with pytest.raises(ValueError):
            validate_hours_periods(period)

    valid_periods = [
        ['15:00-17:00', '12:30-14:00'],
        ['8:00-09:00'],
    ]
    for period in valid_periods:
        validate_hours_periods(period)
