from typing import List

from py_flat_orm.domain.definition.abstract_orm_domain import AbstractOrmDomain
from py_flat_orm.domain.definition.orm_mapping import OrmMapping
from py_flat_orm.domain.definition.orm_validate import OrmValidate
from py_flat_orm.domain.validation.orm_constraint import OrmConstraint
from py_flat_orm.domain.validation.orm_error_collector import OrmErrorCollector


class MyPerson(AbstractOrmDomain):
    def __init__(self, **kwargs):
        self.id: int = kwargs.get('id')
        self.name: str = kwargs.get('name')

    def resolve_mappings(self) -> List[OrmMapping]:
        return OrmMapping.map_domain(MyPerson, [
            OrmMapping.create('id', 'serial'),
            OrmMapping.create('name', 'usercode'),
        ])

    def validate(self) -> 'OrmErrorCollector':
        item = OrmErrorCollector.create(self)
        OrmValidate.with_rule(item, 'id', [OrmConstraint.required()])
        OrmValidate.with_rule(item, 'name', [OrmConstraint.required()])
        OrmValidate.if_satisfies(lambda x: x['id'] == 1).then(item, 'name', [OrmConstraint.min_length(5)])
        return item

    def table_name(self) -> str:
        return 'mis_users'

    @staticmethod
    def list_by_name_starts_with(session, prefix: str) -> List['MyPerson']:
        sql = f"select * from mis_users where usercode like {prefix}%"
        return []
