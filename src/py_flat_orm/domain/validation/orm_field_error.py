from typing import Any, Dict

from py_flat_orm.domain.validation.orm_constraint import OrmConstraint  # type: ignore


class OrmFieldError:
    def __init__(self, constraint: OrmConstraint, field: str, invalid_value: Any):
        self.constraint = constraint
        self.field = field
        self.invalid_value = invalid_value

    @staticmethod
    def create(constraint: OrmConstraint, field: str, invalid_value: Any) -> 'OrmFieldError':
        return OrmFieldError(constraint, field, invalid_value)

    def to_dict(self) -> Dict[str, Any]:
        m: Dict[str, Any] = {'field': self.field}
        m['constraint'] = self.constraint.constraint_type
        if self.constraint.value is not None:
            m['constraint_value'] = self.constraint.value
        if self.constraint.values:
            m['constraint_values'] = ', '.join(map(str, self.constraint.values))
        m['invalid_value'] = self.invalid_value
        return m
