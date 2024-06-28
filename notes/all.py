from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import List, Any, Dict
from datetime import datetime
from in_fn import InFn
from id_gen import IdGen
from domain_util import DomainUtil

Base = declarative_base()

class OrmDomain:
    def resolve_mappings(self) -> List:
        pass

    def validate(self) -> 'OrmErrorCollector':
        pass

    def get_id(self) -> int:
        pass

    def set_id(self, id: int):
        pass

    def table_name(self) -> str:
        pass

class OrmMapping:
    def __init__(self, camel_field_name: str, db_field_name: str):
        self.camel_field_name = camel_field_name
        self.db_field_name = db_field_name.lower()

    @staticmethod
    def create(camel_field_name: str, db_field_name: str) -> 'OrmMapping':
        return OrmMapping(camel_field_name, db_field_name)

    @staticmethod
    def map_domain(a_class: type, custom_mapping: List['OrmMapping'] = None) -> List['OrmMapping']:
        defaults = OrmMapping.create_domain_default(a_class)
        items = (custom_mapping + defaults) if custom_mapping else defaults
        return sorted(set(items), key=lambda x: x.db_field_name)

    @staticmethod
    def create_domain_default(a_class: type) -> List['OrmMapping']:
        obj = a_class()
        map_obj = InFn.to_map(obj)
        return [OrmMapping.create(field, InFn.camel_to_upper_snake_case(field)) for field in map_obj.keys()]

    @staticmethod
    def to_domain(db_domain_field_mappings: List['OrmMapping'], result_set: Dict[str, Any], create_domain_fn):
        props = {
            mapping.camel_field_name: InFn.safe_get(None, lambda: result_set[mapping.db_field_name])
            for mapping in db_domain_field_mappings
        }
        return create_domain_fn(props)

    @staticmethod
    def split_id_and_non_id_mappings(mappings: List['OrmMapping']) -> List[List['OrmMapping']]:
        id_mapping = next((m for m in mappings if m.camel_field_name.lower() == 'id'), None)
        non_id_mappings = [m for m in mappings if m.camel_field_name != id_mapping.camel_field_name]
        return [[id_mapping], non_id_mappings]

    @staticmethod
    def get_id_mapping(mappings: List['OrmMapping']) -> 'OrmMapping':
        return OrmMapping.split_id_and_non_id_mappings(mappings)[0][0]

class OrmFieldError:
    def __init__(self, constraint: OrmConstraint, field: str, invalid_value: Any):
        self.constraint = constraint
        self.field = field
        self.invalid_value = invalid_value

    @staticmethod
    def create(constraint: OrmConstraint, field: str, invalid_value: Any) -> 'OrmFieldError':
        return OrmFieldError(constraint, field, invalid_value)

    def to_map(self) -> Dict[str, Any]:
        m = {'field': self.field, 'constraint': self.constraint.type.value}
        if self.constraint.value is not None:
            m['constraintValue'] = self.constraint.value
        if self.constraint.values:
            m['constraintValues'] = ', '.join(map(str, self.constraint.values))
        m['invalidValue'] = self.invalid_value
        return m

class OrmFieldErrors:
    def __init__(self, field: str):
        self.field = field
        self.errors = []

    @staticmethod
    def create(field: str) -> 'OrmFieldErrors':
        return OrmFieldErrors(field)

    def add_error(self, field_error: OrmFieldError) -> 'OrmFieldErrors':
        self.errors.append(field_error)
        return self

    def has_errors(self) -> bool:
        return bool(self.errors)


class ConnectionUtil:
    @staticmethod
    def get_connection(driver_class_name: str, url: str, connection_properties: Dict[str, str]):
        try:
            engine = create_engine(url, **connection_properties)
            return engine.connect()
        except Exception as ex:
            raise RuntimeError(str(ex)) from ex

    @staticmethod
    def close(connection):
        try:
            if connection:
                connection.close()
        except Exception:
            pass  # Ignore close failures


class MyPerson(Base, OrmDomain):
    __tablename__ = 'mis_users'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def resolve_mappings(self) -> List[OrmMapping]:
        return OrmMapping.map_domain(MyPerson, [
            OrmMapping.create('id', 'serial'),
            OrmMapping.create('name', 'usercode'),
        ])

    def validate(self) -> 'OrmErrorCollector':
        item = OrmErrorCollector.create(self)
        OrmValidate.with_(item, 'id', [required()])
        OrmValidate.with_(item, 'name', [required()])
        OrmValidate.if_satisfies(lambda: self.id == 1).then(item, 'name', [min_length(5)])
        return item

    def table_name(self) -> str:
        return 'mis_users'

    @staticmethod
    def list_by_name_starts_with(session, prefix: str) -> List['MyPerson']:
        return session.query(MyPerson).filter(MyPerson.name.like(f"{prefix}%")).all()

class RepoDb:
    @staticmethod
    def get_conn():
        try:
            return RepoDb.create_target_db_connection()
        except Exception as ex:
            raise RuntimeError(f"Failed to create database connection: {str(ex)}") from ex

    @staticmethod
    def create_target_db_connection():
        # Implement connection creation logic here
        pass

class AbstractOrmDomain(OrmDomain):
    def resolve_mappings(self) -> List[OrmMapping]:
        return OrmMapping.map_domain(self.__class__, [])

    @staticmethod
    def count(session, a_class: type) -> int:
        return session.query(a_class).count()

    @staticmethod
    def list_all(session, a_class: type) -> List[Any]:
        return session.query(a_class).all()

    @staticmethod
    def get_by_id(session, a_class: type, id: int) -> Any:
        return session.query(a_class).get(id)

    @staticmethod
    def get_first(session, a_class: type, select_statement: str) -> Any:
        return session.query(a_class).filter(select_statement).first()

    def validate_and_save(self, session) -> 'OrmErrorCollector':
        return OrmWrite.validate_and_save(session, self)

    def insert_or_update(self, session) -> 'OrmDomain':
        return OrmWrite.insert_or_update(session, self)

    def delete(self, session) -> bool:
        return OrmWrite.delete(session, self)

class OrmRead:
    @staticmethod
    def list_all(session, a_class: type) -> List[Any]:
        return session.query(a_class).all()

    @staticmethod
    def count(session, a_class: type) -> int:
        return session.query(a_class).count()

    @staticmethod
    def get_by_id(session, a_class: type, id: int) -> Any:
        return session.query(a_class).get(id)

    @staticmethod
    def get_first(session, a_class: type, select_statement: str) -> Any:
        return session.query(a_class).filter(select_statement).first()

from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, Float, BigDecimal
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import List, Any, Dict, TypeVar
from datetime import datetime
from in_fn import InFn
from id_gen import IdGen
from domain_util import DomainUtil

Base = declarative_base()

class OrmWrite:
    @staticmethod
    def validate_and_save(session, domain: OrmDomain) -> 'OrmErrorCollector':
        error_collector = domain.validate()
        if not error_collector.has_errors():
            OrmWrite.insert_or_update(session, domain)
        return error_collector

    @staticmethod
    def delete(session, domain: OrmDomain) -> bool:
        statement = OrmWrite.create_delete_prepared_statement(session, domain)
        rows_affected = statement.execute()
        return rows_affected > 0

    @staticmethod
    def insert_or_update(session, domain: OrmDomain) -> OrmDomain:
        is_new = IdGen.is_generated_id(domain.get_id())
        if is_new:
            statement = OrmWrite.create_insert_prepared_statement(session, domain)
            rows_affected = statement.execute()
            if rows_affected > 0:
                id_mapping = OrmMapping.get_id_mapping(domain.resolve_mappings())
                domain.set_id(OrmWrite.resolve_id(statement.inserted_primary_key, id_mapping))
        else:
            statement = OrmWrite.create_update_prepared_statement(session, domain)
            statement.execute()
        return domain

    @staticmethod
    def create_insert_prepared_statement(session, domain: OrmDomain):
        id_and_non_id_mappings = OrmMapping.split_id_and_non_id_mappings(domain.resolve_mappings())
        non_id_mappings = id_and_non_id_mappings[1]
        sql = OrmWrite.create_insert_statement(domain.table_name(), non_id_mappings)
        statement = session.execute(sql)
        statement = OrmWrite.set_statement_params(statement, domain, non_id_mappings)
        return statement

    @staticmethod
    def create_update_prepared_statement(session, domain: OrmDomain):
        id_and_non_id_mappings = OrmMapping.split_id_and_non_id_mappings(domain.resolve_mappings())
        id_mapping = id_and_non_id_mappings[0][0]
        non_id_mappings = id_and_non_id_mappings[1]
        sql = OrmWrite.create_update_statement(domain.table_name(), domain.get_id(), id_mapping, non_id_mappings)
        statement = session.execute(sql)
        statement = OrmWrite.set_statement_params(statement, domain, non_id_mappings)
        return statement

    @staticmethod
    def create_delete_prepared_statement(session, domain: OrmDomain):
        id_and_non_id_mappings = OrmMapping.split_id_and_non_id_mappings(domain.resolve_mappings())
        id_mapping = id_and_non_id_mappings[0][0]
        sql = OrmWrite.create_delete_statement(domain.table_name(), id_mapping)
        statement = session.execute(sql)
        statement.bindparams(domain.get_id())
        return statement

    @staticmethod
    def create_insert_statement(table_name: str, non_id_mappings: List[OrmMapping]) -> str:
        field_names = ', '.join([m.db_field_name for m in non_id_mappings])
        value_placeholders = ', '.join(['?' for _ in non_id_mappings])
        return f"INSERT INTO {table_name.lower()} ({field_names}) VALUES ({value_placeholders})"

    @staticmethod
    def create_update_statement(table_name: str, id: int, id_mapping: OrmMapping, non_id_mappings: List[OrmMapping]) -> str:
        set_statement = ', '.join([f"{m.db_field_name} = ?" for m in non_id_mappings])
        return f"UPDATE {table_name.lower()} SET {set_statement} WHERE {id_mapping.db_field_name} = {id}"

    @staticmethod
    def create_delete_statement(table_name: str, id_mapping: OrmMapping) -> str:
        return f"DELETE FROM {table_name.lower()} WHERE {id_mapping.db_field_name} = ?"

    @staticmethod
    def set_statement_params(statement, domain: OrmDomain, non_id_mappings: List[OrmMapping]):
        for index, mapping in enumerate(non_id_mappings):
            one_based_position = index + 1
            type_ = InFn.get_type(domain.__class__, mapping.camel_field_name)
            value = getattr(domain, mapping.camel_field_name)
            if type_ == bool:
                statement = statement.bindparams(one_based_position, InFn.prop_as_boolean(mapping.camel_field_name, domain))
            elif type_ == BigDecimal:
                statement = statement.bindparams(one_based_position, InFn.prop_as_big_decimal(mapping.camel_field_name, domain))
            elif type_ == Date:
                statement = statement.bindparams(one_based_position, InFn.prop_as_date(mapping.camel_field_name, domain))
            elif type_ == float:
                statement = statement.bindparams(one_based_position, InFn.prop_as_float(mapping.camel_field_name, domain))
            elif type_ == int:
                statement = statement.bindparams(one_based_position, InFn.prop_as_integer(mapping.camel_field_name, domain))
            elif type_ == str:
                statement = statement.bindparams(one_based_position, InFn.prop_as_string(mapping.camel_field_name, domain))
        return statement

    @staticmethod
    def resolve_id(inserted_primary_key, id_mapping: OrmMapping) -> int:
        if not id_mapping:
            raise UnsupportedOperationException('Missing OrmMapping for id')
        return inserted_primary_key[0]

class OrmActor:
    @staticmethod
    def run(engine, fn):
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            result = fn(session)
            session.commit()
            return result
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def run_in_tx(engine, fn):
        return OrmActor.run(engine, fn)

    @staticmethod
    def terminate():
        raise Exception('Terminate transaction and rollback')

class OrmErrorCollector:
    def __init__(self, domain: Any):
        self.domain = domain
        self.fields = {}

    @staticmethod
    def create(domain: Any) -> 'OrmErrorCollector':
        return OrmErrorCollector(domain)

    def add_error(self, field_error: OrmFieldError):
        field = field_error.field
        if field not in self.fields:
            self.fields[field] = OrmFieldErrors.create(field)
        self.fields[field].add_error(field_error)

    def has_errors(self) -> bool:
        return any(field_errors.has_errors() for field_errors in self.fields.values())

    @staticmethod
    def have_errors(collectors: List['OrmErrorCollector']) -> bool:
        return any(collector.has_errors() for collector in collectors)

    @staticmethod
    def to_error_maps(collectors: List['OrmErrorCollector']) -> List[Dict[str, Any]]:
        return [collector.to_map() for collector in collectors if collector.has_errors()]

    def to_map(self) -> Dict[str, Any]:
        return {field: field_errors.errors for field, field_errors in self.fields.items()}


class OrmValidate:
    @staticmethod
    def with_(collector: OrmErrorCollector, field: str, constraints: List[OrmConstraint]):
        value = getattr(collector.domain, field)
        for constraint in constraints:
            OrmValidate.collect_error(collector, constraint, field, value)
        return collector

    @staticmethod
    def collect_error(collector: OrmErrorCollector, constraint: OrmConstraint, field: str, value: Any):
        if not OrmConstraint.is_valid(constraint, value):
            field_error = OrmFieldError.create(constraint, field, value)
            collector.add_error(field_error)

    @staticmethod
    def if_satisfies(condition):
        class ConditionalValidator:
            def __init__(self, condition):
                self.condition = condition

            def then(self, collector: OrmErrorCollector, field: str, constraints: List[OrmConstraint]):
                if self.condition():
                    OrmValidate.with_(collector, field, constraints)

        return ConditionalValidator(condition)



from enum import Enum

class OrmConstraintType(Enum):
    REQUIRED = 'REQUIRED'
    MINIMUM_LENGTH = 'MINIMUM_LENGTH'
    MINIMUM_VALUE = 'MINIMUM_VALUE'
    MAXIMUM_VALUE = 'MAXIMUM_VALUE'
    IN_LIST = 'IN_LIST'
    NOT_IN_LIST = 'NOT_IN_LIST'
    UNIQUE = 'UNIQUE'


from typing import List, Optional, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Date, Float, BigDecimal
from in_fn import InFn
from id_gen import IdGen
from domain_util import DomainUtil
from datetime import datetime

Base = declarative_base()

class OrmConstraint:
    def __init__(self, type: OrmConstraintType, value: Optional[str] = None, values: Optional[List[Any]] = None):
        self.type = type
        self.value = value
        self.values = values

    @staticmethod
    def required() -> 'OrmConstraint':
        return OrmConstraint(type=OrmConstraintType.REQUIRED)

    @staticmethod
    def min_length(value: int) -> 'OrmConstraint':
        return OrmConstraint(type=OrmConstraintType.MINIMUM_LENGTH, value=str(value))

    @staticmethod
    def min_value(value: int) -> 'OrmConstraint':
        return OrmConstraint(type=OrmConstraintType.MINIMUM_VALUE, value=str(value))

    @staticmethod
    def max_value(value: int) -> 'OrmConstraint':
        return OrmConstraint(type=OrmConstraintType.MAXIMUM_VALUE, value=str(value))

    @staticmethod
    def in_list(values: List[Any]) -> 'OrmConstraint':
        return OrmConstraint(type=OrmConstraintType.IN_LIST, values=values)

    @staticmethod
    def not_in_list(values: List[Any]) -> 'OrmConstraint':
        return OrmConstraint(type=OrmConstraintType.NOT_IN_LIST, values=values)

    @staticmethod
    def is_valid(constraint: 'OrmConstraint', v: Any) -> bool:
        if constraint.type == OrmConstraintType.REQUIRED:
            return bool(v and str(v).strip())
        elif constraint.type == OrmConstraintType.MINIMUM_LENGTH:
            return v is None or len(str(v)) >= int(constraint.value)
        elif constraint.type == OrmConstraintType.MINIMUM_VALUE:
            return v is None or (InFn.is_number(v) and InFn.as_long(v) >= int(constraint.value))
        elif constraint.type == OrmConstraintType.MAXIMUM_VALUE:
            return v is None or (InFn.is_number(v) and InFn.as_long(v) <= int(constraint.value))
        elif constraint.type == OrmConstraintType.IN_LIST:
            return v is None or v in constraint.values
        elif constraint.type == OrmConstraintType.NOT_IN_LIST:
            return v is None or v not in constraint.values
        else:
            return True


import unittest
from my_person import MyPerson
from orm_error_collector import OrmErrorCollector

class TestMyPerson(unittest.TestCase):

    def test_creation(self):
        self.assertIsNotNone(MyPerson())

    def test_validate(self):
        # Given
        person = MyPerson(id=1, name='Andy')

        # When
        domain_errors = person.validate()

        # Then
        self.assertTrue(domain_errors.has_errors())
        expected_errors = {
            'name': [
                {
                    'constraint': 'MINIMUM_LENGTH',
                    'constraintValue': '5',
                    'field': 'name',
                    'invalidValue': 'Andy'
                }
            ]
        }
        self.assertEqual(domain_errors.to_map(), expected_errors)

class TestOrmValidate(unittest.TestCase):

    def test_if_satisfies_required(self):
        test_cases = [
            (40, 'Andy', True),
            (40, None, False),
            (20, 'Andy', True),
            (20, None, True),
            (None, 'Andy', True),
            (None, None, True)
        ]

        for age, name, is_valid in test_cases:
            with self.subTest(age=age, name=name, is_valid=is_valid):
                person = MyPerson(name=name, age=age)
                item = OrmErrorCollector.create(person)
                OrmValidate.if_satisfies(lambda: person.age > 35).then(item, 'name', [OrmConstraint.required()])
                self.assertEqual(not item.has_errors(), is_valid)

    def test_if_satisfies_min_length(self):
        test_cases = [
            (40, 'Andy', True),
            (40, 'Yo', False),
            (40, None, True),
            (20, 'Andy', True),
            (20, None, True),
            (None, 'Andy', True),
            (None, None, True)
        ]

        for age, name, is_valid in test_cases:
            with self.subTest(age=age, name=name, is_valid=is_valid):
                person = MyPerson(name=name, age=age)
                item = OrmErrorCollector.create(person)
                OrmValidate.if_satisfies(lambda: person.age > 35).then(item, 'name', [OrmConstraint.min_length(3)])
                self.assertEqual(not item.has_errors(), is_valid)

    def test_if_satisfies_min_max_value(self):
        test_cases = [
            ('Andy', 18, True),
            ('Andy', 17, False),
            ('Andy', None, True),
            ('Andy', 80, True),
            ('Andy', 81, False),
            ('Bob', 18, True),
            ('Bob', 17, True),
            ('Bob', None, True),
            ('Bob', 80, True),
            ('Bob', 81, True)
        ]

        for name, age, is_valid in test_cases:
            with self.subTest(name=name, age=age, is_valid=is_valid):
                person = MyPerson(name=name, age=age)
                item = OrmErrorCollector.create(person)
                OrmValidate.if_satisfies(lambda: person.name == 'Andy').then(item, 'age', [OrmConstraint.min_value(18), OrmConstraint.max_value(80)])
                self.assertEqual(not item.has_errors(), is_valid)

    def test_if_satisfies_in_list(self):
        test_cases = [
            ('Andy', 'male', True),
            ('Andy', 'M', False),
            ('Andy', None, True),
            ('Bob', 'male', True),
            ('Bob', 'M', True),
            ('Bob', None, True)
        ]

        for name, gender, is_valid in test_cases:
            with self.subTest(name=name, gender=gender, is_valid=is_valid):
                person = MyPerson(name=name, gender=gender)
                item = OrmErrorCollector.create(person)
                OrmValidate.if_satisfies(lambda: person.name == 'Andy').then(item, 'gender', [OrmConstraint.in_list(['male', 'female'])])
                self.assertEqual(not item.has_errors(), is_valid)

    def test_if_satisfies_not_in_list(self):
        test_cases = [
            ('Andy', 'male', False),
            ('Andy', 'M', True),
            ('Andy', None, True),
            ('Bob', 'male', True),
            ('Bob', 'M', True),
            ('Bob', None, True)
        ]

        for name, gender, is_valid in test_cases:
            with self.subTest(name=name, gender=gender, is_valid=is_valid):
                person = MyPerson(name=name, gender=gender)
                item = OrmErrorCollector.create(person)
                OrmValidate.if_satisfies(lambda: person.name == 'Andy').then(item, 'gender', [OrmConstraint.not_in_list(['male', 'female'])])
                self.assertEqual(not item.has_errors(), is_valid)

if __name__ == '__main__':
    unittest.main()


import unittest
from orm_mapping import OrmMapping
from my_person import MyPerson
from unittest.mock import Mock

class TestOrmMapping(unittest.TestCase):

    def test_map_domain(self):
        # When
        items = OrmMapping.map_domain(MyPerson, [
            OrmMapping.create('id', 'SERIAL'),
        ])

        # Then
        camel_field_names = [item.camel_field_name for item in items]
        db_field_names = [item.db_field_name for item in items]
        self.assertIn('id', camel_field_names)
        self.assertIn('name', camel_field_names)
        self.assertIn('SERIAL', db_field_names)
        self.assertIn('NAME', db_field_names)

    def test_create_method(self):
        test_cases = [
            ("name", "NAME"),
            ("age", "AGE"),
            ("address", "ADDRESS")
        ]

        for camel_field_name, db_field_name in test_cases:
            with self.subTest(camel_field_name=camel_field_name, db_field_name=db_field_name):
                orm_mapping = OrmMapping.create(camel_field_name, db_field_name)
                self.assertEqual(orm_mapping.camel_field_name, camel_field_name)
                self.assertEqual(orm_mapping.db_field_name, db_field_name)

    def test_map_domain_with_default_mappings(self):
        # Given
        expected_mappings = [
            OrmMapping.create("name", "NAME"),
            OrmMapping.create("age", "AGE"),
            OrmMapping.create("active", "ACTIVE")
        ]

        # When
        mappings = OrmMapping.map_domain(TestDomain)

        # Then
        self.assertEqual(len(mappings), len(expected_mappings))
        camel_field_names = [item.camel_field_name for item in mappings]
        db_field_names = [item.db_field_name for item in mappings]
        expected_camel_field_names = [item.camel_field_name for item in expected_mappings]
        expected_db_field_names = [item.db_field_name for item in expected_mappings]
        self.assertTrue(all(name in camel_field_names for name in expected_camel_field_names))
        self.assertTrue(all(name in db_field_names for name in expected_db_field_names))

    def test_map_domain_with_custom_mappings(self):
        # Given
        custom_mappings = [OrmMapping.create("custom_field", "CUSTOM_FIELD")]
        expected_mappings = custom_mappings + [
            OrmMapping.create("name", "NAME"),
            OrmMapping.create("age", "AGE"),
            OrmMapping.create("active", "ACTIVE")
        ]

        # When
        mappings = OrmMapping.map_domain(TestDomain, custom_mappings)

        # Then
        self.assertEqual(len(mappings), len(expected_mappings))
        camel_field_names = [item.camel_field_name for item in mappings]
        db_field_names = [item.db_field_name for item in mappings]
        expected_camel_field_names = [item.camel_field_name for item in expected_mappings]
        expected_db_field_names = [item.db_field_name for item in expected_mappings]
        self.assertTrue(all(name in camel_field_names for name in expected_camel_field_names))
        self.assertTrue(all(name in db_field_names for name in expected_db_field_names))

    def test_to_domain_method(self):
        # Given
        result_set = Mock()
        result_set.getObject.side_effect = lambda x: {
            "NAME": "John",
            "AGE": 25,
            "ACTIVE": True
        }[x]

        mappings = [
            OrmMapping.create("name", "NAME"),
            OrmMapping.create("age", "AGE"),
            OrmMapping.create("active", "ACTIVE")
        ]

        # When
        domain = OrmMapping.to_domain(mappings, result_set, lambda props: TestDomain(props))

        # Then
        self.assertEqual(domain.name, "John")
        self.assertEqual(domain.age, 25)
        self.assertTrue(domain.active)

class TestDomain:
    def __init__(self, props):
        self.name = props.get('name')
        self.age = props.get('age')
        self.active = props.get('active')

if __name__ == '__main__':
    unittest.main()


import unittest
from unittest.mock import Mock, MagicMock
from orm_write import OrmWrite
from my_person import MyPerson
from orm_error_collector import OrmErrorCollector
from orm_domain import OrmDomain

class TestOrmWrite(unittest.TestCase):

    def test_validate_and_save(self):
        # Given
        conn = Mock()
        person = MyPerson(id=1, name='Andy')

        # When
        error_collector = OrmWrite.validate_and_save(conn, person)

        # Then
        self.assertTrue(error_collector.has_errors())
        expected_errors = {
            'name': [
                {
                    'constraint': 'MINIMUM_LENGTH',
                    'constraintValue': '5',
                    'field': 'name',
                    'invalidValue': 'Andy'
                }
            ]
        }
        self.assertEqual(error_collector.to_map(), expected_errors)

    def test_delete(self):
        # Given
        conn = Mock()
        person = MyPerson(id=1, name='Andy')

        # When
        result = OrmWrite.delete(conn, person)

        # Then
        self.assertTrue(result)

    def test_insert_or_update(self):
        # Given
        conn = Mock()
        person = MyPerson(id=1, name='Andy')

        # When
        result = OrmWrite.insert_or_update(conn, person)

        # Then
        self.assertEqual(result, person)

if __name__ == '__main__':
    unittest.main()


import unittest
from unittest.mock import Mock, patch
from repo_db import RepoDb
from orm_actor import OrmActor
from orm_read import OrmRead
from my_person import MyPerson

class TestRepoDb(unittest.TestCase):

    @patch('repo_db.RepoDb.conn')
    def test_run(self, mock_conn):
        # Given
        people1 = []
        people2 = []
        person = None
        count = 0

        def mock_run(connection):
            nonlocal people1, people2, person, count
            people1 = OrmRead.list_all(connection, MyPerson)
            people2 = MyPerson.list_by_name_starts_with(connection, 'A')  # custom sql
            person = OrmRead.get_by_id(connection, MyPerson, 1)
            count = OrmRead.count(connection, MyPerson)

        OrmActor.run(RepoDb.conn, mock_run)

        # Then
        self.assertGreater(len(people1), 0)
        self.assertGreater(len(people2), 0)
        self.assertIsNotNone(person)
        self.assertGreater(count, 0)

    @patch('repo_db.RepoDb.conn')
    def test_run_in_tx(self, mock_conn):
        # Given
        people1 = []
        people2 = []
        person = None

        def mock_run_in_tx(connection):
            nonlocal people1, people2, person
            people1 = OrmRead.list_all(connection, MyPerson)
            people2 = MyPerson.list_by_name_starts_with(connection, 'A')  # custom sql
            person = OrmRead.get_by_id(connection, MyPerson, 1)

        OrmActor.run_in_tx(RepoDb.conn, mock_run_in_tx)

        # Then
        self.assertGreater(len(people1), 0)
        self.assertGreater(len(people2), 0)
        self.assertIsNotNone(person)

if __name__ == '__main__':
    unittest.main()


import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from repo_db import RepoDb
from orm_actor import OrmActor
from orm_read import OrmRead
from orm_write import OrmWrite
from orm_error_collector import OrmErrorCollector
from my_person import MyPerson
from id_gen import IdGen

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MyApp:
    @staticmethod
    def main():
        MyApp.run_without_tx()
        MyApp.run_with_tx()

    @staticmethod
    def run_without_tx():
        def run(conn):
            logger.info('run')
            id_gen = IdGen.create()
            people1 = OrmRead.list_all(conn, MyPerson)
            people2 = MyPerson.list_by_name_starts_with(conn, 'An')
            person = OrmRead.get_by_id(conn, MyPerson, 1)
            logger.info(OrmRead.count(conn, MyPerson))
            logger.info(', '.join([p.name for p in people1]))
            logger.info(', '.join([p.name for p in people2]))
            logger.info(person.name if person else None)
            p = MyPerson(id=id_gen.get_int(), name='Andrew')
            collector = OrmWrite.validate_and_save(conn, p)
            logger.info(p.id)
            logger.info(collector.has_errors())
            logger.info(OrmRead.count(conn, MyPerson))
            is_deleted = OrmWrite.delete(conn, p)
            logger.info(is_deleted)
            logger.info(OrmRead.count(conn, MyPerson))

        OrmActor.run(RepoDb.get_conn(), run)

    @staticmethod
    def run_with_tx():
        error_map = {}

        def run_in_tx(conn):
            logger.info('runInTx')
            id_gen = IdGen.create()
            logger.info(OrmRead.count(conn, MyPerson))
            collector1 = OrmWrite.validate_and_save(conn, MyPerson(id=id_gen.get_int(), name='Bobby'))
            logger.info(OrmRead.count(conn, MyPerson))
            p = MyPerson(name='Christine')
            collector2 = OrmWrite.validate_and_save(conn, p)
            logger.info(OrmRead.count(conn, MyPerson))
            people = [collector1, collector2]
            have_errors = OrmErrorCollector.have_errors(people)
            if have_errors:
                error_map['people'] = OrmErrorCollector.to_error_maps(people)
                OrmActor.terminate()

        OrmActor.run_in_tx(RepoDb.get_conn(), run_in_tx)
        logger.info(error_map)

if __name__ == '__main__':
    MyApp.main()
