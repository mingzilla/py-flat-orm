"""in_fn"""
import decimal
import re
from datetime import date, time, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, List, Optional, Callable, Type, TypeVar

T = TypeVar('T')


class InFn:

    @staticmethod
    def as_string(obj: Any) -> str | None:
        return str(obj) if obj is not None else None

    @staticmethod
    def as_boolean(obj: Any) -> Optional[bool]:
        if obj is None:
            return None
        return InFn.as_string(obj).strip().lower() == 'true'

    @staticmethod
    def as_decimal(obj: Any) -> Optional[Decimal]:
        string_val = str(obj).strip()
        try:
            return Decimal(string_val)
        except decimal.InvalidOperation:
            return None

    @staticmethod
    def as_decimal_with_scale(decimal_places: Any, mode: Any, obj: Any) -> Optional[Decimal]:
        decimals = InFn.as_integer(decimal_places)
        decimal = InFn.as_decimal(obj)
        if decimal is not None and decimals is not None:
            return decimal.quantize(Decimal('1.' + '0' * decimals), rounding=mode)
        return decimal

    @staticmethod
    def as_double(obj: Any) -> Optional[float]:
        string_val = str(obj).strip()
        try:
            return float(string_val)
        except ValueError:
            return None

    @staticmethod
    def as_float(obj: Any) -> Optional[float]:
        string_val = str(obj).strip()
        try:
            return float(string_val)
        except ValueError:
            return None

    @staticmethod
    def as_integer(obj: Any) -> Optional[int]:
        string_val = str(obj).strip()
        try:
            return int(string_val)
        except ValueError:
            return None

    @staticmethod
    def as_long(obj: Any) -> Optional[int]:
        return InFn.as_integer(obj)

    @staticmethod
    def safe_get(default_value: Any, fn: Callable) -> Any:
        try:
            return fn()
        except Exception:
            return default_value

    @staticmethod
    def has_field(field_name: str, o: Any) -> bool:
        if o is None:
            return False
        if isinstance(o, dict):
            return field_name in o
        return hasattr(o, field_name)

    @staticmethod
    def is_blank(value: str) -> bool:
        return not bool(value and value.strip())

    @staticmethod
    def is_not_blank(value: str) -> bool:
        return bool(value and value.strip())

    @staticmethod
    def is_decimal(obj: Any) -> bool:
        return InFn.as_decimal(obj) is not None

    @staticmethod
    def is_boolean(obj: Any) -> bool:
        val = InFn.as_string(obj)
        if val is None: return False
        return val.lower() in ['true', 'false']

    @staticmethod
    def is_double(obj: Any) -> bool:
        return InFn.as_double(obj) is not None

    @staticmethod
    def is_float(obj: Any) -> bool:
        return InFn.as_float(obj) is not None

    @staticmethod
    def is_integer(obj: Any) -> bool:
        return InFn.as_integer(obj) is not None

    @staticmethod
    def is_none(v: Any) -> bool:
        return v is None

    @staticmethod
    def is_number(value: Any) -> bool:
        try:
            float(value)
            return True
        except (TypeError, ValueError):
            return False

    @staticmethod
    def get_enum_keys(a_class: type, custom_exclude_fields: List[str] = None) -> List[str]:
        excludes = (custom_exclude_fields or []) + ['__class__', '__doc__', '__module__', '__weakref__', '__members__', '__name__', '__qualname__']
        return [prop for prop in dir(a_class) if prop not in excludes and not callable(getattr(a_class, prop))]

    @staticmethod
    def get_keys(o: Any) -> List[str]:
        if o is None:
            return []
        if isinstance(o, type) and issubclass(o, Enum):
            return InFn.get_enum_keys(o)
        props = o if isinstance(o, dict) else vars(o)
        return [k for k in props.keys() if k != 'class']

    @staticmethod
    def get_static_field_type(clazz: Type[Any], field: str) -> Type[Any] | None:
        try:
            return clazz.__annotations__[field]
        except KeyError:
            return None

    @staticmethod
    def camel_to_upper_snake_case(text: str) -> Optional[str]:
        return re.sub(r'(?<!^)(?=[A-Z])', '_', text).upper().lstrip('_') if text else None

    @staticmethod
    def prop_as_string(name: str, obj: Any) -> Optional[str]:
        return InFn.as_string(InFn.prop(name, obj or {}))

    @staticmethod
    def camel_to_lower_hyphen_case(text: str) -> Optional[str]:
        return re.sub(r'(?<!^)(?=[A-Z])', '-', text).lower().lstrip('-') if text else None

    @staticmethod
    def hyphen_to_snake_case(text: str) -> Optional[str]:
        return text.replace('-', '_') if text else None

    @staticmethod
    def snake_to_hyphen_case(text: str) -> Optional[str]:
        return text.replace('_', '-') if text else None

    @staticmethod
    def prop_as_boolean(name: str, obj: Any) -> Optional[bool]:
        return InFn.as_boolean(InFn.prop_as_string(name, obj))

    @staticmethod
    def prop_as_decimal(name: str, obj: Any) -> Optional[Decimal]:
        return InFn.as_decimal(InFn.prop_as_string(name, obj))

    @staticmethod
    def prop_as_double(name: str, obj: Any) -> Optional[float]:
        return InFn.as_double(InFn.prop_as_string(name, obj))

    @staticmethod
    def prop_as_float(name: str, obj: Any) -> Optional[float]:
        return InFn.as_float(InFn.prop_as_string(name, obj))

    @staticmethod
    def prop_as_integer(name: str, obj: Any) -> Optional[int]:
        return InFn.as_integer(InFn.prop_as_string(name, obj))

    @staticmethod
    def prop_as_long(name: str, obj: Any) -> Optional[int]:
        return InFn.as_long(InFn.prop_as_string(name, obj))

    @staticmethod
    def self(x: Any) -> Any:
        return x

    @staticmethod
    def uniq_by(items: List[T], prop_fn: Callable[[T], Any]) -> List[T]:
        item_map = {}
        for item in items:
            prop = prop_fn(item)
            if prop not in item_map:
                item_map[prop] = item
        return list(item_map.values())

    @staticmethod
    def to_dict(o: Any, custom_exclude_fields: Optional[List[str]] = None) -> dict:
        exclude_fields = custom_exclude_fields or []
        keys = InFn.get_keys(o) if o else []

        result = {k: getattr(o, k) for k in keys if k not in exclude_fields}

        if 'id' not in exclude_fields and InFn.has_field('id', o):
            result['id'] = getattr(o, 'id')

        return result

    @staticmethod
    def prop(name: str, o: Any) -> Any:
        if name is None:
            return None
        if isinstance(o, dict):
            return o.get(name)
        return getattr(o, name, None)

    @staticmethod
    def to_date(value: Any) -> date:
        if isinstance(value, datetime):
            return value.date()
        elif isinstance(value, date):
            return value
        elif isinstance(value, time):
            # Create a datetime object with the current date and given time
            current_date = datetime.now().date()
            dt = datetime.combine(current_date, value)
            return dt.date()
        else:
            raise TypeError("Unsupported type. Expected date, time, or datetime object.")

    @staticmethod
    def to_time(value: Any) -> time:
        if isinstance(value, datetime):
            return value.time()
        else:
            raise TypeError("Unsupported type. Expected datetime object.")

    @staticmethod
    def to_datetime(value: Any) -> datetime:
        if isinstance(value, datetime):
            return value
        elif isinstance(value, date):
            # Combine date with default time (midnight)
            return datetime.combine(value, datetime.min.time())
        elif isinstance(value, time):
            # Create a date object (current date)
            current_date = datetime.now().date()
            # Combine date and time to create datetime
            return datetime.combine(current_date, value)
        else:
            raise TypeError("Unsupported type. Expected date, time, or datetime object.")

    @staticmethod
    def set_primitive_field(obj: Any, field_name: str, value: Any) -> Any:
        if obj is None or field_name is None:
            return obj

        if not InFn.has_field(field_name, obj):
            return obj

        if value is None:
            setattr(obj, field_name, None)
            return obj

        try:
            obj_fields = type(obj)()

            val_to_check = obj_fields.__dict__[field_name]

            if isinstance(val_to_check, int):
                setattr(obj, field_name, int(value))
            elif isinstance(val_to_check, float):  # after int check: int is float, float is not int
                setattr(obj, field_name, float(value))
            elif isinstance(val_to_check, bool):
                setattr(obj, field_name, bool(value))
            elif isinstance(val_to_check, str):
                setattr(obj, field_name, str(value))
            elif isinstance(val_to_check, datetime):
                setattr(obj, field_name, InFn.to_datetime(value))
            elif isinstance(val_to_check, date):  # after datetime check: datetime is date, date is not datetime
                setattr(obj, field_name, InFn.to_date(value))
            elif isinstance(val_to_check, time):
                setattr(obj, field_name, InFn.to_time(value))
            elif InFn.has_field(field_name, obj):
                setattr(obj, field_name, value)

        except TypeError:
            pass  # Field does not exist

        return obj

    @staticmethod
    def spaced_to_lower_snake_case(text: str) -> Optional[str]:
        return text.strip().lower().replace(" ", "_") if text else None

    @staticmethod
    def trim_to_empty_if_is_string(v: Any) -> Any:
        if not isinstance(v, str):
            return v
        return v.strip() if v is not None else None

    @staticmethod
    def without_char(obj: Any) -> str:
        if obj is None:
            return ''
        return re.sub(r'[a-zA-Z]+', '', str(obj))
