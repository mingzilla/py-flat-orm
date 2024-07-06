from typing import List, TypeVar, Optional

from sqlalchemy.engine import Connection

from py_flat_orm.domain.definition.orm_domain import OrmDomain
from py_flat_orm.domain.definition.orm_mapping import OrmMapping
from py_flat_orm.domain.orm_read import OrmRead
from py_flat_orm.domain.orm_write import OrmWrite
from py_flat_orm.domain.validation.orm_error_collector import OrmErrorCollector

T = TypeVar('T', bound='AbstractOrmDomain')

class AbstractOrmDomain(OrmDomain):

    def get_id(self) -> int:
        return self['id']

    def set_id(self, id_value: int):
        self['id'] = id_value

    def resolve_mappings(self) -> List[OrmMapping]:
        return OrmMapping.map_domain(self.__class__, [])

    def get_id_mapping(self) -> OrmMapping:
        return OrmMapping.get_id_mapping(self.resolve_mappings())

    def count(self, conn: Connection) -> int:
        return OrmRead.count(conn, self.__class__)

    def list_all(self: T, conn: Connection) -> List[T]:
        return OrmRead.list_all(conn, self.__class__)

    def get_by_id(self: T, conn: Connection, id_value: int) -> Optional[T]:
        return OrmRead.get_by_id(conn, self.__class__, id_value)

    def get_first(self: T, conn: Connection, select_statement: str, params: dict) -> Optional[T]:
        return OrmRead.get_first(conn, self.__class__, select_statement, params)

    def validate_and_save(self, conn: Connection) -> OrmErrorCollector:
        return OrmWrite.validate_and_save(conn, self)

    def insert_or_update(self, conn: Connection) -> OrmDomain:
        return OrmWrite.insert_or_update(conn, self)

    def delete(self, conn: Connection) -> bool:
        return OrmWrite.delete(conn, self)
