from sqlalchemy import text, Connection

from py_flat_orm.domain.definition.orm_domain import OrmDomain
from py_flat_orm.domain.definition.orm_mapping import OrmMapping
from py_flat_orm.domain.validation.orm_error_collector import OrmErrorCollector
from py_flat_orm.util.base_util.id_gen import IdGen


class OrmWrite:

    @staticmethod
    def validate_and_save(conn: Connection, domain: OrmDomain) -> OrmErrorCollector:
        error_collector = domain.validate()
        if not error_collector.has_errors():
            OrmWrite.insert_or_update(conn, domain)
        return error_collector

    @staticmethod
    def delete(conn: Connection, domain: OrmDomain) -> bool:
        statement = f"delete FROM {domain.table_name()} where {domain.get_id_mapping().db_field_name} = {domain.get_id()}"
        result = conn.execute(text(statement))
        return result.rowcount > 0

    @staticmethod
    def insert_or_update(conn: Connection, domain: OrmDomain) -> OrmDomain:
        is_new = IdGen.is_generated_id(domain.get_id())
        if is_new:
            return OrmWrite.insert(conn, domain)
        else:
            return OrmWrite.update(conn, domain)

    @staticmethod
    def insert(conn: Connection, domain: OrmDomain) -> OrmDomain:
        mappings = domain.resolve_mappings()
        table_name = domain.table_name().lower()

        id_mappings, non_id_mappings = OrmMapping.split_id_and_non_id_mappings(mappings)
        field_names = ', '.join(map(lambda m: m.db_field_name, non_id_mappings))
        values = ', '.join(map(lambda m: f":{m.db_field_name}", non_id_mappings))
        params = OrmDomain.to_params(domain, non_id_mappings)

        statement = f"insert into {table_name} ({field_names}) values ({values})"
        result = conn.execute(text(statement), params)
        domain.set_id(result.lastrowid)
        return domain

    @staticmethod
    def update(conn: Connection, domain: OrmDomain) -> OrmDomain:
        mappings = domain.resolve_mappings()
        table_name = domain.table_name().lower()

        id_mappings, non_id_mappings = OrmMapping.split_id_and_non_id_mappings(mappings)
        field_names = ', '.join(map(lambda m: m.db_field_name, non_id_mappings))
        values = ', '.join(map(lambda m: f":{m.db_field_name}", non_id_mappings))
        params = OrmDomain.to_params(domain, non_id_mappings)

        statement = f"update {table_name} ({field_names}) values ({values}) WHERE {id_mappings[0].db_field_name} = {domain.get_id()}"
        conn.execute(text(statement), params)
        return domain
