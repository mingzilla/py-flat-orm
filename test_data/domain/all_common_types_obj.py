from py_flat_orm.util.base_util.in_val import InVal


class AllCommonTypesObj:

    def __init__(self):
        self.int_field = InVal.int_field
        self.float_field = InVal.float_field
        self.bool_field = InVal.bool_field
        self.str_field = InVal.str_field
        self.date_field = InVal.date_field
        self.time_field = InVal.time_field
        self.datetime_field = InVal.datetime_field
