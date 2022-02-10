import unittest
import numpy as np
from parameterized import parameterized

from robocup.spec.specification import FieldSpecificationAdultSize
from robocup.rules.field import *


class TestFieldModel(unittest.TestCase):

    def setUp(self) -> None:
        self.field_model = FieldModel(FieldSpecificationAdultSize())

    @parameterized.expand([
        [-28, 40, 56, 36],

    ])
    def test__init_side_line(self, expected_side_line_x, expected_side_line_y, expected_side_line_width,
                             expected_side_line_height):
        side_line_data = self.field_model.side_line_data
        self.assertEqual(side_line_data['side_line_x'], expected_side_line_x)
        self.assertEqual(side_line_data['side_line_y'], expected_side_line_y)
        self.assertEqual(side_line_data['side_line_width'], expected_side_line_width)
        self.assertEqual(side_line_data['side_line_height'], expected_side_line_height)

    @parameterized.expand([
        [-0.1, 40, 0.2, 36, 0, 22, 1.5 * 4],

    ])
    def test__init_middle_line(self, expected_middle_line_x, expected_middle_line_y, expected_middle_line_width,
                               expected_middle_line_height, expected_circle_x, expected_circle_y, expected_circle_r):
        middle_line_data = self.field_model.middle_line_data
        self.assertEqual(middle_line_data['middle_line_x'], expected_middle_line_x)
        self.assertEqual(middle_line_data['middle_line_y'], expected_middle_line_y)
        self.assertEqual(middle_line_data['middle_line_width'], expected_middle_line_width)
        self.assertEqual(middle_line_data['middle_line_height'], expected_middle_line_height)

        self.assertEqual(middle_line_data['circle_x'], expected_circle_x)
        self.assertEqual(middle_line_data['circle_y'], expected_circle_y)
        self.assertEqual(middle_line_data['circle_r'], expected_circle_r)

    @parameterized.expand([
        [-28, 34, 12, 24, 16],

    ])
    def test___init_penalty_area(self, expected_penalty_area_left_x, expected_penalty_area_y,
                                 expected_penalty_area_width, expected_penalty_area_height,
                                 expected_penalty_area_right_x):
        penalty_area_data = self.field_model.penalty_area_data

        self.assertEqual(penalty_area_data['penalty_area_left_x'], expected_penalty_area_left_x)
        self.assertEqual(penalty_area_data['penalty_area_y'], expected_penalty_area_y)
        self.assertEqual(penalty_area_data['penalty_area_width'], expected_penalty_area_width)
        self.assertEqual(penalty_area_data['penalty_area_height'], expected_penalty_area_height)

        self.assertEqual(penalty_area_data['penalty_area_right_x'], expected_penalty_area_right_x)

    @parameterized.expand([
        [-28, 30, 4, 16, 24],

    ])
    def test___init_goal_area(self, expected_goal_area_left_x, expected_goal_area_y,
                              expected_goal_area_width, expected_goal_area_height,
                              expected_goal_area_right_x):
        goal_area_data = self.field_model.goal_area_data

        self.assertEqual(goal_area_data['goal_area_left_x'], expected_goal_area_left_x)
        self.assertEqual(goal_area_data['goal_area_y'], expected_goal_area_y)
        self.assertEqual(goal_area_data['goal_area_width'], expected_goal_area_width)
        self.assertEqual(goal_area_data['goal_area_height'], expected_goal_area_height)

        self.assertEqual(goal_area_data['goal_area_right_x'], expected_goal_area_right_x)


if __name__ == '__main__':
    unittest.main()
