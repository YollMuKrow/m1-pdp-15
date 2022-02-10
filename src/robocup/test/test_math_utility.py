import unittest


from robocup.utility.math_utility import *

from parameterized import parameterized


class TestMathUtility(unittest.TestCase):

    @parameterized.expand([
        [25, 10, 20, 20, 10, 10, 10, {'left': False, 'right': False, 'up': False, 'down': False}],
        [10, 10, 10, 10, 10, 10, 10, {'left': False, 'right': False, 'up': False, 'down': True}],
    ])
    def test_collision_rectangle_circle(self, rect_x, rect_y, rect_width, rect_height, circle_x, circle_y, circle_radius, solution):
        self.assertTrue(collision_rectangle_circle(rect_x, rect_y, rect_width, rect_height, circle_x, circle_y, circle_radius) == solution)

    @parameterized.expand([
        [10, 10, 0, 0, 90, -10, 10],
    ])
    def test_rotate_point(self, point_x, point_y, origin_x, origin_y, angle, sol_x, sol_y):
        self.assertEqual(
            (rotate_point(point_x, point_y, origin_x, origin_y, angle).x,
             rotate_point(point_x, point_y, origin_x, origin_y, angle).y), (sol_x, sol_y))

    @parameterized.expand([
        [10, 10, 0, 10, 10, (20, 10)],
        [15, 30, 90, 20, 20, (15, 50)],
    ])
    def test_convert_coordinates_with_angle_and_radius(self, point_x, point_y, origin_angle, radius_x, radius_y, solution):
        self.assertEqual(round(convert_coordinates_with_angle_and_radius(point_x, point_y, origin_angle, radius_x, radius_y).x), solution[0])
        self.assertEqual(round(convert_coordinates_with_angle_and_radius(point_x, point_y, origin_angle, radius_x, radius_y).y), solution[1])

    @parameterized.expand([
        [10, 10, 10, 0, 0, 15, True],
        [15, 30, 9, 40, 70, 15, False],
    ])
    def test_collision_circle_circle(self, circle1_x, circle1_y, circle1_radius, circle2_x, circle2_y, circle2_radius, solution):
        self.assertEqual(collision_circle_circle( circle1_x, circle1_y, circle1_radius, circle2_x, circle2_y, circle2_radius), solution)
