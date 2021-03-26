class InvalidDataError(ValueError):
    pass


class OrderForCourierNotExist(InvalidDataError):
    def __str__(self):
        return 'Courier does not have such order.'


class OrderAlreadyCompleted(InvalidDataError):
    def __str__(self):
        return 'The order has already been completed'


class InvalidCompleteTime(InvalidDataError):
    def __str__(self):
        return 'Invalid complete time.'
