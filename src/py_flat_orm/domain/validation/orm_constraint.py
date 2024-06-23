from typing import List, Optional, Any

from py_flat_orm.domain.validation.orm_constraint_type import OrmConstraintType  # type: ignore
from py_flat_orm.util.base_util.in_fn import InFn  # type: ignore


class OrmConstraint:
    def __init__(self, type_: OrmConstraintType, value: Optional[str] = None, values: Optional[List[Any]] = None):
        self.type = type_
        self.value = value
        self.values = values

    @staticmethod
    def required() -> 'OrmConstraint':
        return OrmConstraint(type_=OrmConstraintType.REQUIRED)

    @staticmethod
    def min_length(value: int) -> 'OrmConstraint':
        return OrmConstraint(type_=OrmConstraintType.MINIMUM_LENGTH, value=str(value))

    @staticmethod
    def min_value(value: int) -> 'OrmConstraint':
        return OrmConstraint(type_=OrmConstraintType.MINIMUM_VALUE, value=str(value))

    @staticmethod
    def max_value(value: int) -> 'OrmConstraint':
        return OrmConstraint(type_=OrmConstraintType.MAXIMUM_VALUE, value=str(value))

    @staticmethod
    def in_list(values: List[Any]) -> 'OrmConstraint':
        return OrmConstraint(type_=OrmConstraintType.IN_LIST, values=values)

    @staticmethod
    def not_in_list(values: List[Any]) -> 'OrmConstraint':
        return OrmConstraint(type_=OrmConstraintType.NOT_IN_LIST, values=values)

    @staticmethod
    def is_valid(constraint: 'OrmConstraint', v: Any) -> bool:
        if constraint.type == OrmConstraintType.REQUIRED:
            return InFn.is_not_blank(str(v))
        elif constraint.type == OrmConstraintType.MINIMUM_LENGTH:
            return v is None or len(str(v or '')) >= InFn.as_integer(constraint.value)
        elif constraint.type == OrmConstraintType.MINIMUM_VALUE:
            return v is None or (InFn.is_number(v) and InFn.as_long(v) >= InFn.as_integer(constraint.value))
        elif constraint.type == OrmConstraintType.MAXIMUM_VALUE:
            return v is None or (InFn.is_number(v) and InFn.as_long(v) <= InFn.as_integer(constraint.value))
        elif constraint.type == OrmConstraintType.IN_LIST:
            return v is None or v in constraint.values  # type: ignore
        elif constraint.type == OrmConstraintType.NOT_IN_LIST:
            return v is None or v not in constraint.values  # type: ignore
        else:
            return True
