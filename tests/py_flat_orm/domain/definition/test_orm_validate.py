import unittest

from py_flat_orm.domain.definition.orm_validate import OrmValidate
from py_flat_orm.domain.validation.orm_constraint import OrmConstraint
from py_flat_orm.domain.validation.orm_error_collector import OrmErrorCollector
from test_data.domain.orm_validate_test_domain import OrmValidateTestDomainPerson


class TestOrmValidate(unittest.TestCase):

    def test_required(self):
        test_cases = [
            ('name', None, False),
            ('name', '', False),
            ('name', 'Andy', True)
        ]
        for field, value, is_valid in test_cases:
            with self.subTest(field=field, value=value, is_valid=is_valid):
                item = OrmErrorCollector.create(OrmValidateTestDomainPerson(**{field: value}))
                OrmValidate.with_rule(item, 'name', [OrmConstraint.required()])
                self.assertEqual(not item.has_errors(), is_valid)

    def test_min_length(self):
        test_cases = [
            ('name', 'Andy', True),
            ('name', 'Yo', False),
            ('name', None, True)
        ]
        for field, value, is_valid in test_cases:
            with self.subTest(field=field, value=value, is_valid=is_valid):
                item = OrmErrorCollector.create(OrmValidateTestDomainPerson(**{field: value}))
                OrmValidate.with_rule(item, 'name', [OrmConstraint.min_length(3)])
                self.assertEqual(not item.has_errors(), is_valid)

    def test_min_max_value(self):
        test_cases = [
            ('age', 18, True),
            ('age', 17, False),
            ('age', None, True),
            ('age', 80, True),
            ('age', 81, False)
        ]
        for field, value, is_valid in test_cases:
            with self.subTest(field=field, value=value, is_valid=is_valid):
                item = OrmErrorCollector.create(OrmValidateTestDomainPerson(**{field: value}))
                OrmValidate.with_rule(item, 'age', [OrmConstraint.min_value(18), OrmConstraint.max_value(80)])
                self.assertEqual(not item.has_errors(), is_valid)

    def test_in_list_text(self):
        test_cases = [
            ('gender', 'male', True),
            ('gender', 'M', False),
            ('gender', None, True)
        ]
        for field, value, is_valid in test_cases:
            with self.subTest(field=field, value=value, is_valid=is_valid):
                item = OrmErrorCollector.create(OrmValidateTestDomainPerson(**{field: value}))
                OrmValidate.with_rule(item, 'gender', [OrmConstraint.in_list(['male', 'female'])])
                self.assertEqual(not item.has_errors(), is_valid)

    def test_in_list_number(self):
        test_cases = [
            ('born_month', 1, True),
            ('born_month', 12, True),
            ('born_month', 0, False),
            ('born_month', 13, False),
            ('born_month', None, True)
        ]
        for field, value, is_valid in test_cases:
            with self.subTest(field=field, value=value, is_valid=is_valid):
                item = OrmErrorCollector.create(OrmValidateTestDomainPerson(**{field: value}))
                OrmValidate.with_rule(item, 'born_month', [OrmConstraint.in_list(range(1, 13))])
                self.assertEqual(not item.has_errors(), is_valid)

    def test_not_in_list_text(self):
        test_cases = [
            ('gender', 'male', False),
            ('gender', 'M', True),
            ('gender', None, True)
        ]
        for field, value, is_valid in test_cases:
            with self.subTest(field=field, value=value, is_valid=is_valid):
                item = OrmErrorCollector.create(OrmValidateTestDomainPerson(**{field: value}))
                OrmValidate.with_rule(item, 'gender', [OrmConstraint.not_in_list(['male', 'female'])])
                self.assertEqual(not item.has_errors(), is_valid)

    def test_not_in_list_number(self):
        test_cases = [
            ('born_month', 1, False),
            ('born_month', 12, False),
            ('born_month', 0, True),
            ('born_month', 13, True),
            ('born_month', None, True)
        ]
        for field, value, is_valid in test_cases:
            with self.subTest(field=field, value=value, is_valid=is_valid):
                item = OrmErrorCollector.create(OrmValidateTestDomainPerson(**{field: value}))
                OrmValidate.with_rule(item, 'born_month', [OrmConstraint.not_in_list(range(1, 13))])
                self.assertEqual(not item.has_errors(), is_valid)

    def test_if_having(self):
        test_cases = [
            ('Andy', None, False),
            ('Andy', '', False),
            ('Andy', 20, True),
            (None, None, True),
            (None, 20, True)
        ]
        for name, age, is_valid in test_cases:
            with self.subTest(name=name, age=age, is_valid=is_valid):
                person = OrmValidateTestDomainPerson(name=name, age=age)
                item = OrmErrorCollector.create(person)
                OrmValidate.if_having('name').then(item, 'age', [OrmConstraint.required()])
                self.assertEqual(not item.has_errors(), is_valid)

    def test_if_not_having(self):
        test_cases = [
            ('Andy', 20, True),
            ('Andy', None, True),
            (None, None, False),
            (None, 20, True)
        ]
        for name, age, is_valid in test_cases:
            with self.subTest(name=name, age=age, is_valid=is_valid):
                person = OrmValidateTestDomainPerson(name=name, age=age)
                item = OrmErrorCollector.create(person)
                OrmValidate.if_not_having('name').then(item, 'age', [OrmConstraint.required()])
                self.assertEqual(not item.has_errors(), is_valid)

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
                person = OrmValidateTestDomainPerson(name=name, age=age)
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
                person = OrmValidateTestDomainPerson(name=name, age=age)
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
                person = OrmValidateTestDomainPerson(name=name, age=age)
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
                person = OrmValidateTestDomainPerson(name=name, gender=gender)
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
                person = OrmValidateTestDomainPerson(name=name, gender=gender)
                item = OrmErrorCollector.create(person)
                OrmValidate.if_satisfies(lambda: person.name == 'Andy').then(item, 'gender', [OrmConstraint.not_in_list(['male', 'female'])])
                self.assertEqual(not item.has_errors(), is_valid)


if __name__ == '__main__':
    unittest.main()
