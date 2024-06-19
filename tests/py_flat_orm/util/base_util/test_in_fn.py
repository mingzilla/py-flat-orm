"""TestInFn"""

import unittest
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from example.my_person import MyPerson
from example.test_enum import TestEnum
from py_flat_orm.util.base_util.in_fn import InFn


class TestInFn(unittest.TestCase):
    """TestInFn"""

    def test_as_boolean(self):
        self.assertIsNone(InFn.as_boolean(None))
        self.assertTrue(InFn.as_boolean('true'))
        self.assertFalse(InFn.as_boolean('false'))
        self.assertFalse(InFn.as_boolean('any other string'))

    def test_as_big_decimal(self):
        self.assertEqual(InFn.as_big_decimal('123.456'), Decimal('123.456'))
        self.assertIsNone(InFn.as_big_decimal('not a number'))

    def test_as_big_decimal_with_scale(self):
        self.assertEqual(
            InFn.as_big_decimal_with_scale(2, ROUND_HALF_UP, '123.456'),
            Decimal('123.46')
        )
        self.assertIsNone(InFn.as_big_decimal_with_scale(2, ROUND_HALF_UP, 'not a number'))

    def test_as_double(self):
        self.assertEqual(InFn.as_double('123.456'), 123.456)
        self.assertIsNone(InFn.as_double('not a number'))

    def test_as_float(self):
        self.assertEqual(InFn.as_float('123.456'), 123.456)
        self.assertIsNone(InFn.as_float('not a number'))

    def test_as_integer(self):
        self.assertEqual(InFn.as_integer('123'), 123)
        self.assertIsNone(InFn.as_integer('not a number'))

    def test_as_long(self):
        self.assertEqual(InFn.as_long('123'), 123)
        self.assertIsNone(InFn.as_long('not a number'))

    def test_as_string(self):
        self.assertEqual(InFn.as_string(123), '123')
        self.assertEqual(InFn.as_string(None), None)

    def test_safe_get(self):
        self.assertEqual(InFn.safe_get(42, lambda: 1 / 0), 42)
        self.assertEqual(InFn.safe_get(42, lambda: 21 * 2), 42)

    def test_has_field(self):
        self.assertTrue(InFn.has_field('key', {'key': 'value'}))
        self.assertFalse(InFn.has_field('key', {}))

    def test_is_big_decimal(self):
        self.assertTrue(InFn.is_big_decimal('123.456'))
        self.assertFalse(InFn.is_big_decimal('not a number'))

    def test_is_big_integer(self):
        self.assertTrue(InFn.is_big_integer('123456'))
        self.assertFalse(InFn.is_big_integer('123.456'))

    def test_is_boolean(self):
        self.assertTrue(InFn.is_boolean('true'))
        self.assertTrue(InFn.is_boolean('false'))
        self.assertFalse(InFn.is_boolean('maybe'))

    def test_is_double(self):
        self.assertTrue(InFn.is_double('123.456'))
        self.assertFalse(InFn.is_double('not a number'))

    def test_is_float(self):
        self.assertTrue(InFn.is_float('123.456'))
        self.assertFalse(InFn.is_float('not a number'))

    def test_is_integer(self):
        self.assertTrue(InFn.is_integer('123'))
        self.assertFalse(InFn.is_integer('123.456'))

    def test_is_long(self):
        self.assertTrue(InFn.is_long('123'))
        self.assertFalse(InFn.is_long('123.456'))

    def test_is_null(self):
        self.assertTrue(InFn.is_none(None))
        self.assertFalse(InFn.is_none('123'))

    def test_is_number(self):
        self.assertTrue(InFn.is_number('123'))
        self.assertTrue(InFn.is_number('123.456'))
        self.assertFalse(InFn.is_number('not a number'))

    def test_get_enum_keys(self):
        expected_keys = ['ONE', 'TWO', 'THREE']
        result = InFn.get_enum_keys(TestEnum)
        self.assertListEqual(sorted(result), sorted(expected_keys))

    def test_get_keys(self):
        class DummyClass:
            def __init__(self):
                self.field1 = 'value1'
                self.field2 = 'value2'

        self.assertEqual(InFn.get_keys(DummyClass()), ['field1', 'field2'])

    def test_get_type(self):
        self.assertEqual(InFn.get_type(MyPerson, "id"), int | None)
        self.assertEqual(InFn.get_type(MyPerson, "age"), int)
        self.assertEqual(InFn.get_type(MyPerson, "name"), str)
        self.assertEqual(InFn.get_type(MyPerson, "is_male"), bool)
        self.assertEqual(InFn.get_type(MyPerson, "is_single"), bool | None)
        self.assertEqual(InFn.get_type(MyPerson, "long_v"), int)
        self.assertEqual(InFn.get_type(MyPerson, "long_v2"), int | None)

    # Optional: Use subTest for parameterized tests
    def test_get_type_parametrized(self):
        parameters = [
            ("id", int | None),
            ("age", int),
            ("name", str),
            ("is_male", bool),
            ("is_single", bool | None),
            ("long_v", int),
            ("long_v2", int | None)
        ]

        for field_name, expected_type in parameters:
            with self.subTest(field_name=field_name):
                self.assertEqual(InFn.get_type(MyPerson, field_name), expected_type)

    def test_camel_to_upper_snake_case(self):
        self.assertEqual(InFn.camel_to_upper_snake_case('camelCaseText'), 'CAMEL_CASE_TEXT')
        self.assertIsNone(InFn.camel_to_upper_snake_case(None))

    def test_prop_as_string(self):
        self.assertEqual(InFn.prop_as_string('key', {'key': 'value'}), 'value')
        self.assertIsNone(InFn.prop_as_string('key', {}))

    def test_camel_to_lower_hyphen_case(self):
        self.assertEqual(InFn.camel_to_lower_hyphen_case('camelCaseText'), 'camel-case-text')
        self.assertIsNone(InFn.camel_to_lower_hyphen_case(None))

    def test_hyphen_to_snake_case(self):
        self.assertEqual(InFn.hyphen_to_snake_case('hyphen-case-text'), 'hyphen_case_text')
        self.assertIsNone(InFn.hyphen_to_snake_case(None))

    def test_snake_to_hyphen_case(self):
        self.assertEqual(InFn.snake_to_hyphen_case('snake_case_text'), 'snake-case-text')
        self.assertIsNone(InFn.snake_to_hyphen_case(None))

    def test_prop_as_boolean(self):
        self.assertTrue(InFn.prop_as_boolean('key', {'key': 'true'}))
        self.assertFalse(InFn.prop_as_boolean('key', {'key': 'false'}))
        self.assertIsNone(InFn.prop_as_boolean('key', {}))

    def test_prop_as_big_decimal(self):
        self.assertEqual(InFn.prop_as_big_decimal('key', {'key': '123.456'}), Decimal('123.456'))
        self.assertIsNone(InFn.prop_as_big_decimal('key', {}))

    def test_prop_as_double(self):
        self.assertEqual(InFn.prop_as_double('key', {'key': '123.456'}), 123.456)
        self.assertIsNone(InFn.prop_as_double('key', {}))

    def test_prop_as_float(self):
        self.assertEqual(InFn.prop_as_float('key', {'key': '123.456'}), 123.456)
        self.assertIsNone(InFn.prop_as_float('key', {}))

    def test_prop_as_integer(self):
        self.assertEqual(InFn.prop_as_integer('key', {'key': '123'}), 123)
        self.assertIsNone(InFn.prop_as_integer('key', {}))

    def test_prop_as_long(self):
        self.assertEqual(InFn.prop_as_long('key', {'key': '123'}), 123)
        self.assertIsNone(InFn.prop_as_long('key', {}))

    def test_self(self):
        self.assertEqual(InFn.self('test'), 'test')

    def test_to_map(self):
        class DummyClass:
            def __init__(self):
                self.field1 = 'value1'
                self.field2 = 'value2'

        expected_map = {'field1': 'value1', 'field2': 'value2'}
        self.assertEqual(InFn.to_map(DummyClass()), expected_map)

    def test_prop(self):
        self.assertEqual(InFn.prop('key', {'key': 'value'}), 'value')
        self.assertIsNone(InFn.prop('key', {}))

    class Person:
        age = 0
        height = 0.0 # `height: float` does not make it a float field, the only way for python to know the type is by forcing a value into a field
        is_active = False
        dob = date(2023, 6, 19)

    def test_set_primitive_field(self):
        obj = TestInFn.Person()

        # Set primitive fields using InFn.set_primitive_field
        InFn.set_primitive_field(obj, "age", 25)
        InFn.set_primitive_field(obj, "height", 1.75)
        InFn.set_primitive_field(obj, "is_active", True)
        InFn.set_primitive_field(obj, "hi", True)
        InFn.set_primitive_field(obj, "dob", date(2024, 6, 19))

        # Assert the fields are set correctly
        self.assertEqual(obj.age, 25)
        self.assertEqual(obj.height, 1.75)
        self.assertTrue(obj.is_active)
        self.assertEqual(obj.dob, date(2024, 6, 19))

    def test_spaced_to_lower_snake_case(self):
        self.assertEqual(InFn.spaced_to_lower_snake_case('test case'), 'test_case')
        self.assertIsNone(InFn.spaced_to_lower_snake_case(None))

    def test_trim_to_empty_if_is_string(self):
        self.assertEqual(InFn.trim_to_empty_if_is_string('  test  '), 'test')
        self.assertEqual(InFn.trim_to_empty_if_is_string(123), 123)
        self.assertIsNone(InFn.trim_to_empty_if_is_string(None))

    def test_without_char(self):
        self.assertEqual(InFn.without_char('abc123'), '123')
        self.assertEqual(InFn.without_char(None), '')


if __name__ == '__main__':
    unittest.main()
