from abc import ABC, abstractmethod  # type: ignore
from typing import List

from py_flat_orm.domain.definition.orm_mapping import OrmMapping
from py_flat_orm.domain.validation.orm_error_collector import OrmErrorCollector
from py_flat_orm.util.base_util.in_fn import InFn


class OrmDomain(ABC):
    @abstractmethod
    def resolve_mappings(self) -> List['OrmMapping']:
        pass

    @abstractmethod
    def validate(self) -> 'OrmErrorCollector':
        pass

    @abstractmethod
    def get_id(self) -> int:
        pass

    @abstractmethod
    def set_id(self, id: int) -> None:
        pass

    @abstractmethod
    def table_name(self) -> str:
        pass

    @abstractmethod
    def get_id_mapping(self) -> 'OrmMapping':
        pass

    @staticmethod
    def to_params(domain: 'OrmDomain', non_id_mappings: List['OrmMapping']) -> dict:
        return {m.db_field_name: InFn.prop(m.domain_field_name, domain) for m in non_id_mappings}
