# Python does not make a field int by doing e.g. `age: int`. Without assignment, the field is not even present
# The only reliable way to make a field int is by setting a value to it
# This allows type checking, e.g.
# if age is 0, isinstance(person.age, int) returns True
# if age is None, isinstance(person.age, int) returns False

from datetime import date, time, datetime


class InVal:
    int_field = 0
    float_field = 0.0
    bool_field = False
    str_field = ''
    date_field = date(2000, 1, 1)
    time_field = time(0, 0, 0)
    datetime_field = datetime(2000, 1, 1, 0, 0, 1)
