"""TestValueUtil"""

import unittest

from py_flat_orm.util.base_util import value_util


class TestValueUtil(unittest.TestCase):
    """TestValueUtil"""

    def test_is_string(self):
        """test_is_string"""
        self.assertEqual(value_util.is_string("hello"), True)
        self.assertEqual(value_util.is_string(123), False)
        self.assertEqual(value_util.is_string([1, 2, 3]), False)
        self.assertEqual(value_util.is_string({"key": "value"}), False)


if __name__ == "__main__":
    unittest.main()
