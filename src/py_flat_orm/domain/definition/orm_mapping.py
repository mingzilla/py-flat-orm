from typing import List, Callable, Type, TypeVar, Optional, Tuple

from py_flat_orm.util.base_util.in_fn import InFn  # type: ignore
from sqlalchemy import Row

T = TypeVar('T')


class OrmMapping:
    def __init__(self, camel_field_name: str, db_field_name: str):
        self.camel_field_name = camel_field_name
        self.db_field_name = db_field_name

    @classmethod
    def create(cls, camel_field_name: str, db_field_name: str) -> 'OrmMapping':
        return cls(camel_field_name, db_field_name.lower())

    @classmethod
    def map_domain(cls, a_class: Type, custom_mapping: Optional[List['OrmMapping']] = None) -> List['OrmMapping']:
        defaults = cls.create_domain_default(a_class)
        items = custom_mapping + defaults if custom_mapping else defaults
        uniq_items = InFn.uniq_by(items, lambda item: item.camel_field_name)
        return sorted(uniq_items, key=lambda x: x.db_field_name)

    @classmethod
    def create_domain_default(cls, a_class: Type) -> List['OrmMapping']:
        obj = a_class()
        fields = InFn.to_dict(obj).keys()
        return [cls.create(field, InFn.camel_to_upper_snake_case(field) or '') for field in fields]

    @staticmethod
    def to_domain(db_domain_field_mappings: List['OrmMapping'], row: Row, create_domain_fn: Callable[[dict], T]) -> T:
        props = {
            mapping.camel_field_name: InFn.safe_get(None, lambda: getattr(row, mapping.db_field_name))
            for mapping in db_domain_field_mappings
        }
        return create_domain_fn(props)

    @classmethod
    def split_id_and_non_id_mappings(cls, mappings: List['OrmMapping']) -> Tuple[List['OrmMapping'], List['OrmMapping']]:
        id_mapping = next((m for m in mappings if m.camel_field_name.lower() == 'id'), None)
        non_id_mappings = [m for m in mappings if m.camel_field_name != id_mapping.camel_field_name] if id_mapping else mappings
        return [id_mapping] if id_mapping else [], non_id_mappings

    @classmethod
    def get_id_mapping(cls, mappings: List['OrmMapping']) -> Optional['OrmMapping']:
        id_and_non_id_mappings = cls.split_id_and_non_id_mappings(mappings)
        return id_and_non_id_mappings[0][0] if id_and_non_id_mappings[0] else None
