from py_flat_orm.util.base_util.in_val import InVal


class AllCommonTypesObj:

    def __init__(self):
        self.int_field = InVal.INT
        self.float_field = InVal.FLOAT
        self.bool_field = InVal.BOOL
        self.str_field = InVal.STR
        self.date_field = InVal.DATE
        self.time_field = InVal.TIME
        self.datetime_field = InVal.DATE_TIME
