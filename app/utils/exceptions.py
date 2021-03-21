class OrderForCourierNotExist(ValueError):
    def __str__(self):
        return 'Courier does not have such order.'
