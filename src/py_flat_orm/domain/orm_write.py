from typing import Any

from sqlalchemy import Table, Column, MetaData, insert, update, delete
from sqlalchemy.engine import Connection

from py_flat_orm.domain.definition.orm_domain import OrmDomain
from py_flat_orm.domain.definition.orm_mapping import OrmMapping
from py_flat_orm.domain.validation.orm_error_collector import OrmErrorCollector
from py_flat_orm.util.base_util.id_gen import IdGen
from py_flat_orm.util.base_util.in_fn import InFn


class OrmWrite:

    @staticmethod
    def validate_and_save(conn: Connection, domain: OrmDomain) -> OrmErrorCollector:
        error_collector = domain.validate()
        if not error_collector.has_errors():
            OrmWrite.insert_or_update(conn, domain)
        return error_collector

    @staticmethod
    def delete(conn: Connection, domain: OrmDomain) -> bool:
        select_statement = f"delete FROM {domain.table_name()} where id = %s"
        statement = OrmWrite.create_delete_statement(domain)
        result = conn.execute(statement)
        return result.rowcount > 0

    @staticmethod
    def insert_or_update(conn: Connection, domain: OrmDomain) -> OrmDomain:
        is_new = IdGen.is_generated_id(domain.id)
        if is_new:
            statement, id_mapping = OrmWrite.create_insert_statement(domain)
            result = conn.execute(statement)
            domain.id = result.inserted_primary_key[0]
        else:
            statement = OrmWrite.create_update_statement(domain)
            conn.execute(statement)
        return domain

    @staticmethod
    def create_insert_statement(domain: OrmDomain) -> (Any, OrmMapping):
        mappings = domain.resolve_mappings()
        non_id_mappings = [m for m in mappings if not m.is_id]
        fields = {m.db_field_name: InFn.prop(m.camel_field_name, domain) for m in non_id_mappings}
        table_name = domain.table_name().lower()
        metadata = MetaData()
        table = Table(table_name, metadata, *[
            Column(m.db_field_name, InFn.get_type(domain.__class__, m.camel_field_name)) for m in non_id_mappings
        ])
        statement = insert(table).values(**fields)
        id_mapping = next(m for m in mappings if m.is_id)
        return statement, id_mapping

    @staticmethod
    def create_update_statement(domain: OrmDomain) -> Any:
        mappings = domain.resolve_mappings()
        id_mapping = next(m for m in mappings if m.is_id)
        non_id_mappings = [m for m in mappings if not m.is_id]
        fields = {m.db_field_name: InFn.prop(m.camel_field_name, domain) for m in non_id_mappings}
        table_name = domain.table_name().lower()
        metadata = MetaData()
        table = Table(table_name, metadata, *[
            Column(m.db_field_name, InFn.get_type(domain.__class__, m.camel_field_name)) for m in non_id_mappings
        ])
        statement = update(table).where(getattr(table.c, id_mapping.db_field_name) == domain.id).values(**fields)
        return statement

    @staticmethod
    def create_delete_statement(domain: OrmDomain) -> Any:
        mappings = domain.resolve_mappings()
        id_mapping = next(m for m in mappings if m.is_id)
        table_name = domain.table_name().lower()
        metadata = MetaData()
        table = Table(table_name, metadata, *[
            Column(m.db_field_name, InFn.get_type(domain.__class__, m.camel_field_name)) for m in mappings
        ])
        statement = delete(table).where(getattr(table.c, id_mapping.db_field_name) == domain.id)
        return statement
