from typing import Callable, List, Type

import sqlalchemy.exc
from sqlalchemy import create_engine, text, Connection, TextClause
from sqlalchemy.orm import Session

from py_flat_orm.domain.definition.orm_domain import OrmDomain
from py_flat_orm.domain.definition.orm_mapping import OrmMapping
from py_flat_orm.util.base_util.domain_util import DomainUtil


class OrmRead:
    NO_PARAMS: Callable[[str], str] = lambda s: s  # Placeholder for no parameter function

    @staticmethod
    def list_all(conn: Connection, cls: Type[OrmDomain]) -> List[OrmDomain]:
        domain = cls()
        query = text(f"SELECT * FROM {domain.table_name()}")

        def create_domain_fn(props: dict):
            return DomainUtil.merge_fields(cls(), props)

        return OrmRead.list_and_merge(conn, domain.resolve_mappings(), query, create_domain_fn)

    @staticmethod
    def list(conn: Connection, cls: Type[OrmDomain], select_statement: str, set_params_fn: Callable[[str], str]) -> List[OrmDomain]:
        domain = cls()
        query = text(f"{select_statement}")

        def create_domain_fn(props: dict):
            return DomainUtil.merge_fields(cls(), props)

        return OrmRead.list_and_merge(conn, domain.resolve_mappings(), query, create_domain_fn)

    @staticmethod
    def list_and_merge(conn: Connection, db_domain_field_mappings: List[OrmMapping], query: TextClause, create_domain_fn: Callable[[dict], OrmDomain]) -> List[OrmDomain]:
        objs = []

        try:
            statement = conn.execute(query)
            for row in statement:
                obj = OrmMapping.to_domain(db_domain_field_mappings, row, create_domain_fn)
                objs.append(obj)
        except sqlalchemy.exc.SQLAlchemyError as sql_ex:
            raise RuntimeError(f"Failed running select statement to create object: {sql_ex}")

        return objs

    @staticmethod
    def get_by_id(engine: create_engine, cls: Type[OrmDomain], id_value: int) -> OrmDomain:
        with Session(engine) as session:
            domain = cls()  # Instantiate the domain class
            mappings = domain.resolve_mappings()

            id_field = next((mapping.db_field_name for mapping in mappings if mapping.camel_field_name == 'id'), None)
            if not id_field:
                raise ValueError("ID field not found in mappings")

            select_statement = text(f"SELECT * FROM {domain.table_name()} WHERE {id_field} = :id")
            params = {'id': id_value}
            return OrmRead.get_and_merge(session, mappings, select_statement, params)

    @staticmethod
    def get_first(engine: create_engine, cls: Type[OrmDomain], select_statement: str) -> OrmDomain:
        with Session(engine) as session:
            domain = cls()  # Instantiate the domain class
            mappings = domain.resolve_mappings()

            return OrmRead.get_and_merge(session, mappings, text(select_statement), OrmRead.NO_PARAMS)

    @staticmethod
    def get_and_merge(session: Session, db_domain_field_mappings: List[OrmMapping], select_statement: str, params: dict) -> OrmDomain:
        try:
            statement = session.execute(select_statement, params)
            row = statement.fetchone()
            if row:
                props = dict(row)
                return db_domain_field_mappings.to_domain(props)
            return None
        except sqlalchemy.exc.SQLAlchemyError as sql_ex:
            raise RuntimeError(f"Failed running select statement to create object: {sql_ex}")

    @staticmethod
    def count(engine: create_engine, cls: Type[OrmDomain]) -> int:
        with Session(engine) as session:
            domain = cls()  # Instantiate the domain class
            select_statement = text(f"SELECT COUNT(*) FROM {domain.table_name()}")
            return OrmRead.get_count(session, select_statement)

    @staticmethod
    def get_count(session: Session, select_statement: str) -> int:
        try:
            statement = session.execute(select_statement)
            return statement.scalar()
        except sqlalchemy.exc.SQLAlchemyError as sql_ex:
            raise RuntimeError(f"Failed running select statement to count records: {sql_ex}")
