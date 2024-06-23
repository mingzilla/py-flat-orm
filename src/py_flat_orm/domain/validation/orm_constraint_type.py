#
from enum import Enum


class OrmConstraintType(Enum):
    REQUIRED = 'REQUIRED'
    MINIMUM_LENGTH = 'MINIMUM_LENGTH'
    MINIMUM_VALUE = 'MINIMUM_VALUE'
    MAXIMUM_VALUE = 'MAXIMUM_VALUE'
    IN_LIST = 'IN_LIST'
    NOT_IN_LIST = 'NOT_IN_LIST'
    UNIQUE = 'UNIQUE'

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value
