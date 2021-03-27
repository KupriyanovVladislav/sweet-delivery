from app.db.schema import CourierTypeEnum

TIME_TEMPLATE = '%H:%M'  # 'HH:MM'

MAX_WEIGHT = 50  # max weight for order
MIN_WEIGHT = 0.01  # min weight for order

COURIER_POWER = {
    CourierTypeEnum.foot: 10,  # Power in kilograms
    CourierTypeEnum.bike: 15,
    CourierTypeEnum.car: 50,
}

COURIER_COEFFICIENT = {
    CourierTypeEnum.foot: 2,  # Coefficient is for computing salary
    CourierTypeEnum.bike: 5,
    CourierTypeEnum.car: 9,
}

NOT_EXISTS_MSG = '{entity} does not exists.'

RFC_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
