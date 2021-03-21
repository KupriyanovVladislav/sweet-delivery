from sqlalchemy import (
    ARRAY, Column, DateTime, Enum as SQLEnum, Float, ForeignKey, Integer, String, Table, MetaData,
)
from datetime import datetime

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

orders_table = Table(
    'orders',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('weight', Float, nullable=False),
    Column('region', Integer, nullable=False),
    Column('delivery_hours', ARRAY(String), nullable=False),
)


couriers_orders_table = Table(
    'couriers_orders',
    metadata,
    Column('courier_id', ForeignKey(couriers_table.c.id), nullable=False),
    Column('order_id', ForeignKey(orders_table.c.id), nullable=False),
    Column('assign_time', DateTime, default=datetime.utcnow, nullable=False),
    Column('complete_time', DateTime, default=None),
    Column('duration', Integer, default=None),
)
