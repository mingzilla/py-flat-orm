from typing import Callable, List, Type, TypeVar, Optional

import sqlalchemy.exc
from sqlalchemy import text, Connection, TextClause

from py_flat_orm.domain.definition.orm_domain import OrmDomain
from py_flat_orm.domain.definition.orm_mapping import OrmMapping
from py_flat_orm.util.base_util.domain_util import DomainUtil

T = TypeVar('T', bound=OrmDomain)


class OrmRead:
    NO_PARAMS: Callable[[str], str] = lambda s: s  # Placeholder for no parameter function

    @staticmethod
    def list_all(conn: Connection, cls: Type[T]) -> List[T]:
        select_statement = f"SELECT * FROM {cls().table_name()}"
        return OrmRead.list(conn, cls, select_statement, {})

    @staticmethod
    def list(conn: Connection, cls: Type[T], select_statement: str, params: dict) -> List[T]:
        domain = cls()
        query = text(f"{select_statement}")

        def create_domain_fn(props: dict):
            return DomainUtil.merge_fields(cls(), props)

        return OrmRead.list_and_merge(conn, domain.resolve_mappings(), query, params, create_domain_fn)

    @staticmethod
    def list_and_merge(conn: Connection, db_domain_field_mappings: List[OrmMapping], query: TextClause, params: dict, create_domain_fn: Callable[[dict], T]) -> List[T]:
        objs = []

        try:
            result = conn.execute(query, params)
            for row in result:
                obj = OrmMapping.to_domain(db_domain_field_mappings, row, create_domain_fn)
                objs.append(obj)
        except sqlalchemy.exc.SQLAlchemyError as sql_ex:
            raise RuntimeError(f"Failed running select statement to create object: {sql_ex}")

        return objs

    @staticmethod
    def get_by_id(conn: Connection, cls: Type[T], id_value: int) -> Optional[T]:
        domain = cls()
        id_mapping = domain.get_id_mapping()
        select_statement = f"SELECT * FROM {domain.table_name()} WHERE {id_mapping.db_field_name} = :id"
        return OrmRead.get_first(conn, cls, select_statement, {'id': id_value})

    @staticmethod
    def get_first(conn: Connection, cls: Type[T], select_statement: str, params: dict) -> Optional[T]:
        domain = cls()
        query = text(f"{select_statement}")

        def create_domain_fn(props: dict):
            return DomainUtil.merge_fields(cls(), props)

        return OrmRead.get_and_merge(conn, domain.resolve_mappings(), query, params, create_domain_fn)

    @staticmethod
    def get_and_merge(conn: Connection, db_domain_field_mappings: List[OrmMapping], query: TextClause, params: dict, create_domain_fn: Callable[[dict], T]) -> Optional[T]:
        try:
            result = conn.execute(query, params)
            row = result.fetchone()
            if row is not None:
                return OrmMapping.to_domain(db_domain_field_mappings, row, create_domain_fn)
            return None
        except sqlalchemy.exc.SQLAlchemyError as sql_ex:
            raise RuntimeError(f"Failed running select statement to create object: {sql_ex}")

    @staticmethod
    def count(conn: Connection, cls: Type[T]) -> int:
        select_statement = text(f"SELECT COUNT(*) FROM {cls().table_name()}")
        return OrmRead.get_count(conn, select_statement)

    @staticmethod
    def get_count(conn: Connection, query: TextClause) -> int:
        try:
            result = conn.execute(query)
            return result.scalar()
        except sqlalchemy.exc.SQLAlchemyError as sql_ex:
            raise RuntimeError(f"Failed running select statement to count records: {sql_ex}")
