import unittest

from py_flat_orm.domain.definition.orm_mapping import OrmMapping


class OrmMappingTest(unittest.TestCase):

    def test_split_id_and_non_id_mappings_with_id(self):
        mappings = [
            OrmMapping('id', 'ID'),
            OrmMapping('name', 'NAME'),
            OrmMapping('age', 'AGE'),
        ]
        id_mappings, non_id_mappings = OrmMapping.split_id_and_non_id_mappings(mappings)

        self.assertEqual(len(id_mappings), 1)
        self.assertEqual(id_mappings[0].camel_field_name, 'id')
        self.assertEqual(len(non_id_mappings), 2)
        self.assertTrue(all(mapping.camel_field_name != 'id' for mapping in non_id_mappings))

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
        self.assertEqual(id_mappings[0].camel_field_name, 'id')
        self.assertEqual(len(non_id_mappings), 3)
        self.assertTrue(all(mapping.camel_field_name != 'id' for mapping in non_id_mappings))


if __name__ == '__main__':
    unittest.main()
