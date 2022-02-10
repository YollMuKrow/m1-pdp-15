import unittest
import numpy as np
from parameterized import parameterized, parameterized_class

from slimevolleygym.slimevolley import check_if_duplicate, invert_dict


class TestUtilityFunctions(unittest.TestCase):

    # @parameterized.expand([
    #     ["foo", "a", "a", ],
    #     ["bar", "a", "a"],
    #     ["lee", "a", "a"],
    # ])
    # def test_sequence(self, name, a, b):
    #     self.assertEqual(a, b)

    @parameterized.expand([
        [[1, 2, 3]],
        [[1, 2, 6]],
        [[1, 3, 6]],
    ])
    def test_check_if_duplicate_should_return_false(self, list_e):
        self.assertEqual(check_if_duplicate(list_e), False)

    @parameterized.expand([
        [[1, 2, 2]],
        [[1, 2, 1]],
        [[2, 2, 2]],
    ])
    def test_check_if_duplicate_should_return_True(self, list_e):
        self.assertEqual(check_if_duplicate(list_e), True)

    @parameterized.expand([
        [[1, 2, 2]],
        [[1, 2, 1]],
        [[2, 2, 2]],
    ])
    def test_check_if_duplicate_should_return_True(self, list_e):
        self.assertEqual(check_if_duplicate(list_e), True)


# @parameterized_class(('a', 'b', 'expected_sum', 'expected_product'), [
#     (1, 2, 3, 2),
#     (5, 5, 10, 25),
# ])
# class TestMathClass(unittest.TestCase):
#     def test_add(self):
#         self.assertEqual(self.a + self.b, self.expected_sum)
#
#     def test_multiply(self):
#         self.assertEqual(self.a * self.b, self.expected_product)


@parameterized_class(('input_dict', 'expected_dict'), [
    ({'yellow': 0}, {0: 'yellow'}),
    ({'white': 1}, {1: 'white'}),
])
class TestInvertDict(unittest.TestCase):
    def test_invert_dict(self):
        result_dict = invert_dict(self.input_dict)
        self.assertDictEqual(result_dict, self.expected_dict)


if __name__ == '__main__':
    unittest.main()
