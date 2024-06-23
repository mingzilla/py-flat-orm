from abc import ABC, abstractmethod
from typing import List

from py_flat_orm.domain.definition.orm_mapping import OrmMapping
from py_flat_orm.domain.validation.orm_error_collector import OrmErrorCollector


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
