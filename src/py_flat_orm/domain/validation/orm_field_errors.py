from typing import List

from py_flat_orm.domain.validation.orm_field_error import OrmFieldError  # type: ignore


class OrmFieldErrors:
    def __init__(self, field: str):
        self.field = field
        self.errors: List[OrmFieldError] = []

    @staticmethod
    def create(field: str) -> 'OrmFieldErrors':
        return OrmFieldErrors(field)

    def add_error(self, field_error: OrmFieldError) -> 'OrmFieldErrors':
        self.errors.append(field_error)
        return self

    def has_errors(self) -> bool:
        return bool(self.errors)
