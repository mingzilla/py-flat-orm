from typing import List

from py_flat_orm.domain.definition.orm_domain import OrmDomain
from py_flat_orm.domain.definition.orm_mapping import OrmMapping
from py_flat_orm.domain.definition.orm_validate import OrmValidate
from py_flat_orm.domain.validation.orm_constraint import OrmConstraint
from py_flat_orm.domain.validation.orm_error_collector import OrmErrorCollector


class OrmValidateTestDomainPerson(OrmDomain):
    def __init__(self, **kwargs):
        self.id: int = kwargs.get('id')
        self.name: str = kwargs.get('name')
        self.age: int = kwargs.get('age')
        self.gender: str = kwargs.get('gender')
        self.born_month: int = kwargs.get('born_month')

    def get_id(self) -> int:
        return self['id']

    def set_id(self, id: int) -> None:
        self['id'] = id

    def resolve_mappings(self) -> List[OrmMapping]:
        return OrmMapping.map_domain(OrmValidateTestDomainPerson, [])

    def validate(self) -> OrmErrorCollector:
        # Example implementation of a validate function
        item = OrmErrorCollector.create(self)

        OrmValidate.with_rule(item, 'name', [OrmConstraint.required(), OrmConstraint.min_length(3)])
        OrmValidate.with_rule(item, 'age', [OrmConstraint.min_value(18), OrmConstraint.max_value(80), OrmConstraint.not_in_list(range(60, 65))])
        OrmValidate.with_rule(item, 'gender', [OrmConstraint.in_list(['male', 'female'])])
        OrmValidate.if_having('name').then(item, 'age', [OrmConstraint.required()])

        return item

    def table_name(self) -> str:
        return 'PERSON'