from sqlalchemy import (
    ARRAY, Column, Enum as SQLEnum, Integer, String, Table, MetaData,
)

from enum import Enum, unique


@unique
class CourierTypeEnum(Enum):
    foot = 'foot'
    bike = 'bike'
    car = 'car'


metadata = MetaData()


couriers_table = Table(
    'couriers',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('type', SQLEnum(CourierTypeEnum, name='type'), nullable=False),
    Column('regions', ARRAY(Integer), nullable=False),
    Column('working_hours', ARRAY(String), nullable=False),
)
