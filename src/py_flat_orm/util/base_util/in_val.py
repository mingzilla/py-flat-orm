# Python does not make a field int by doing e.g. `age: int`. Without assignment, the field is not even present
# The only reliable way to make a field int is by setting a value to it
# This allows type checking, e.g.
# if age is 0, isinstance(person.age, int) returns True
# if age is None, isinstance(person.age, int) returns False

from datetime import date, time, datetime


class InVal:
    INT = 0
    FLOAT = 0.0
    BOOL = False
    STR = ''
    DATE = date(2000, 1, 1)
    TIME = time(0, 0, 0)
    DATE_TIME = datetime(2000, 1, 1, 0, 0, 1)
