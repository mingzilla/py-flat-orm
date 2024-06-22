from unittest import TestCase

from py_flat_orm.util.base_util.id_gen import IdGen


class TestIdGen(TestCase):
    def test_is_generated_id(self):
        id_gen = IdGen.create()
        id = id_gen.get_int()
        self.assertEqual(id_gen.is_generated_id(id), True)
        self.assertEqual(id_gen.is_generated_id(1), False)
        self.assertEqual(id_gen.is_generated_id("Hi"), False)
