from typing import List, Type

from sqlalchemy import create_engine
from sqlalchemy.engine import Connection

from .orm_domain import OrmDomain
from .orm_error_collector import OrmErrorCollector
from .orm_mapping import OrmMapping
from .orm_read import OrmRead
from .orm_write import OrmWrite


class AbstractOrmDomain(OrmDomain):
    def resolve_mappings(self) -> List[OrmMapping]:
        return OrmMapping.map_domain(self.__class__, [])

    @staticmethod
    def count(conn: Connection, a_class: Type['AbstractOrmDomain']) -> int:
        return OrmRead.count(conn, a_class)

    @staticmethod
    def list_all(conn: Connection, a_class: Type['AbstractOrmDomain']) -> List['AbstractOrmDomain']:
        return OrmRead.list_all(conn, a_class)

    @staticmethod
    def get_by_id(conn: Connection, a_class: Type['AbstractOrmDomain'], id: int) -> 'AbstractOrmDomain':
        return OrmRead.get_by_id(conn, a_class, id)

    @staticmethod
    def get_first(conn: Connection, a_class: Type['AbstractOrmDomain'], select_statement: str) -> 'AbstractOrmDomain':
        return OrmRead.get_first(conn, a_class, select_statement)

    def validate_and_save(self, conn: Connection) -> OrmErrorCollector:
        return OrmWrite.validate_and_save(conn, self)

    def insert_or_update(self, conn: Connection) -> OrmDomain:
        return OrmWrite.insert_or_update(conn, self)

    def delete(self, conn: Connection) -> bool:
        return OrmWrite.delete(conn, self)

# Example Usage:
if __name__ == "__main__":
    engine = create_engine('your_database_url')  # Replace 'your_database_url' with your actual database URL
    connection = engine.connect()

    # Example operations
    domain_instance = AbstractOrmDomain()
    mappings = domain_instance.resolve_mappings()
    count = AbstractOrmDomain.count(connection, AbstractOrmDomain)
    all_records = AbstractOrmDomain.list_all(connection, AbstractOrmDomain)
    record_by_id = AbstractOrmDomain.get_by_id(connection, AbstractOrmDomain, 1)
    first_record = AbstractOrmDomain.get_first(connection, AbstractOrmDomain, "SELECT * FROM some_table LIMIT 1")
    error_collector = domain_instance.validate_and_save(connection)
    inserted_or_updated = domain_instance.insert_or_update(connection)
    deleted = domain_instance.delete(connection)

    connection.close()  # Close the connection when done
