import unittest

from py_flat_orm.domain.definition.orm_mapping import OrmMapping
from test_data.domain.orm_mapping_test_domain import OrmMappingTestDomain, OrmMappingCustomDomain


class OrmMappingTest(unittest.TestCase):

    def test_map_domain_with_default_mappings(self):
        expected_mappings = [
            OrmMapping.create("id", "ID"),
            OrmMapping.create("name", "NAME"),
            OrmMapping.create("age", "AGE"),
            OrmMapping.create("active", "ACTIVE"),
        ]

        mappings = OrmMapping.map_domain(OrmMappingTestDomain)

        self.assertEqual(len(mappings), len(expected_mappings))

        expected_domain_field_names = [expected_mapping.domain_field_name for expected_mapping in expected_mappings]
        actual_domain_field_names = [mapping.domain_field_name for mapping in mappings]
        self.assertEqual(set(expected_domain_field_names), set(actual_domain_field_names))

        expected_db_field_names = [expected_mapping.db_field_name for expected_mapping in expected_mappings]
        actual_db_field_names = [mapping.db_field_name for mapping in mappings]
        self.assertEqual(set(expected_db_field_names), set(actual_db_field_names))

    def test_map_domain_with_custom_mappings(self):
        custom_mappings = [OrmMapping.create("custom_field", "CUSTOM_FIELD")]
        expected_mappings = custom_mappings + [
            OrmMapping.create("custom_id", "CUSTOM_ID"),
            OrmMapping.create("name", "NAME"),
        ]

        mappings = OrmMapping.map_domain(OrmMappingCustomDomain, custom_mappings)

        self.assertEqual(len(mappings), len(expected_mappings))

        expected_domain_field_names = [expected_mapping.domain_field_name for expected_mapping in expected_mappings]
        actual_domain_field_names = [mapping.domain_field_name for mapping in mappings]
        self.assertEqual(set(expected_domain_field_names), set(actual_domain_field_names))

        expected_db_field_names = [expected_mapping.db_field_name for expected_mapping in expected_mappings]
        actual_db_field_names = [mapping.db_field_name for mapping in mappings]
        self.assertEqual(set(expected_db_field_names), set(actual_db_field_names))

    def test_split_id_and_non_id_mappings_with_id(self):
        mappings = [
            OrmMapping('id', 'ID'),
            OrmMapping('name', 'NAME'),
            OrmMapping('age', 'AGE'),
        ]
        id_mappings, non_id_mappings = OrmMapping.split_id_and_non_id_mappings(mappings)

        self.assertEqual(len(id_mappings), 1)
        self.assertEqual(id_mappings[0].domain_field_name, 'id')
        self.assertEqual(len(non_id_mappings), 2)
        self.assertTrue(all(mapping.domain_field_name != 'id' for mapping in non_id_mappings))

    def test_split_id_and_non_id_mappings_without_id(self):
        mappings = [
            OrmMapping('name', 'NAME'),
            OrmMapping('age', 'AGE'),
        ]
        id_mappings, non_id_mappings = OrmMapping.split_id_and_non_id_mappings(mappings)

        self.assertEqual(len(id_mappings), 0)
        self.assertEqual(len(non_id_mappings), 2)

    def test_split_id_and_non_id_mappings_with_multiple_potential_ids(self):
        # Only the first 'id' field should be considered the ID mapping
        mappings = [
            OrmMapping('id', 'ID'),
            OrmMapping('anotherId', 'ANOTHER_ID'),
            OrmMapping('name', 'NAME'),
            OrmMapping('age', 'AGE'),
        ]
        id_mappings, non_id_mappings = OrmMapping.split_id_and_non_id_mappings(mappings)

        self.assertEqual(len(id_mappings), 1)
        self.assertEqual(id_mappings[0].domain_field_name, 'id')
        self.assertEqual(len(non_id_mappings), 3)
        self.assertTrue(all(mapping.domain_field_name != 'id' for mapping in non_id_mappings))


if __name__ == '__main__':
    unittest.main()
