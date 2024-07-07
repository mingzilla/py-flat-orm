from typing import List

from py_flat_orm.domain.definition.abstract_orm_domain import AbstractOrmDomain
from py_flat_orm.domain.definition.orm_mapping import OrmMapping
from py_flat_orm.domain.definition.orm_validate import OrmValidate
from py_flat_orm.domain.validation.orm_constraint import OrmConstraint
from py_flat_orm.domain.validation.orm_error_collector import OrmErrorCollector


class Employee(AbstractOrmDomain):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name: str = kwargs.get('name')
        self.age: str = kwargs.get('age')
        self.salary: str = kwargs.get('salary')
        self.birth_date: str = kwargs.get('birth_date')
        self.created_at: str = kwargs.get('created_at')
        self.is_active: str = kwargs.get('is_active')

    def resolve_mappings(self) -> List[OrmMapping]:
        return OrmMapping.map_domain(Employee, [])

    def validate(self) -> 'OrmErrorCollector':
        item = OrmErrorCollector.create(self)
        OrmValidate.with_rule(item, 'id', [OrmConstraint.required()])
        OrmValidate.with_rule(item, 'name', [OrmConstraint.required()])
        return item

    def table_name(self) -> str:
        return 'employees'
