import unittest

from py_flat_orm.util.base_util.domain_util import DomainUtil
from test_data.domain.domain_util_test_domain import DomainUtilTestDomain, DomainUtilTestDomain1


class DomainUtilTest(unittest.TestCase):

    def test_merge_fields(self):
        new_props = [
            {"name": "Jane", "age": 30, "active": False},
            {"name": " "},
            {"age": 40},
            {"active": False},
            {},
            None
        ]
        expected_results = [
            ("Jane", 30, False),
            ("", 25, True),
            ("John", 40, True),
            ("John", 25, False),
            ("John", 25, True),
            ("John", 25, True)
        ]
        for new_prop, expected in zip(new_props, expected_results):
            with self.subTest(new_prop=new_prop):
                obj = DomainUtilTestDomain(name="John", age=25, active=True)
                DomainUtil.merge_fields(obj, new_prop)
                self.assertEqual((obj.name, obj.age, obj.active), expected)

    def test_merge_fields_with_none_and_empty_strings(self):
        new_props = [
            {"name": None},
            {"name": "  ", "age": None},
            {"name": "New Name", "age": 0}
        ]
        expected_results = [
            (None, 25, True),
            ("", None, True),
            ("New Name", 0, True)
        ]
        for new_prop, expected in zip(new_props, expected_results):
            with self.subTest(new_prop=new_prop):
                obj = DomainUtilTestDomain(name="John", age=25, active=True)
                DomainUtil.merge_fields(obj, new_prop)
                self.assertEqual((obj.name, obj.age, obj.active), expected)

    def test_merge_request_data(self):
        original_values = {
            'int1': 5,  # user intentionally sets to 5
            'int2': 5,  # user intentionally sets to 5
            'int3': None,  # user intentionally sets to none
            'text1': None  # user intentionally sets to none
        }
        values = {
            'int1': 5,  # user intentionally sets it to 5, and resolved as 5, use 5
            'int2': 6,  # user intentionally sets it to 5, but resolved as 6, use 6
            'int3': 6,  # user intentionally sets it to none, but resolved as 6 based on business logic, if only 6 is allowed, user cannot remove it
            'text1': None,  # user intentionally sets it to none, and resolved as none, use none
            'text2': None  # user does not have an intention to set it to none, but resolved to none (this is none just because a variable is created without value), should use db value
        }
        obj1 = DomainUtilTestDomain1(int1=1, int2=1, int3=1, text1='X', text2='X')  # values in the db
        new_obj = DomainUtil.merge_request_data(obj1, values, original_values)
        self.assertEqual(new_obj.int1, 5)
        self.assertEqual(new_obj.int2, 6)
        self.assertEqual(new_obj.int3, 6)
        self.assertIsNone(new_obj.text1)
        self.assertEqual(new_obj.text2, 'X')


if __name__ == '__main__':
    unittest.main()
