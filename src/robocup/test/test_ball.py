import unittest

from numpy import sqrt

from robocup.creation.factory import AdultSizeFactory
from robocup.dynamic_object.state import DefaultRelativeState
from robocup.spec.settings import *
from robocup.dynamic_object.ball import Ball
from robocup.rules.field import FieldModel
from robocup.dynamic_object.player import Agent
from parameterized import parameterized


class TestBall(unittest.TestCase):

    def setUp(self) -> None:
        self.ball = Ball(0, 22, 1, BALL_COLOR)

    @parameterized.expand([
        [WINDOW_WIDTH_ADULT_SIZE / 2, WINDOW_HEIGHT_ADULT_SIZE / 2, 10, BALL_COLOR],
        [WINDOW_WIDTH_ADULT_SIZE / 2 + 10, WINDOW_HEIGHT_ADULT_SIZE / 2 + 10, 20, [200, 0, 45]],
    ])
    def test_initialization(self, expected_position_x, expected_position_y, expected_radius, expected_color):
        ball1 = Ball(expected_position_x, expected_position_y, expected_radius, expected_color)
        self.assertIsNotNone(ball1, "Ball initialized")

    @parameterized.expand([
        [Agent(-1, WINDOW_WIDTH_ADULT_SIZE / 2 - 15, WINDOW_HEIGHT_ADULT_SIZE / 2 - 15, 10, 'red', 0,
               DefaultRelativeState())],
        [Agent(-1, WINDOW_WIDTH_ADULT_SIZE / 2 + 15, WINDOW_HEIGHT_ADULT_SIZE / 2 + 15, 10, 'yellow', 0,
               DefaultRelativeState())],
    ])
    def test_ball_is_shot(self, agent):
        initial_speed_x = self.ball.vx
        initial_speed_y = self.ball.vy
        self.ball.ball_is_shot(agent, 10)

        if agent.x < self.ball.x:
            self.assertTrue(initial_speed_x < self.ball.vx)
        else:
            self.assertTrue(initial_speed_x > self.ball.vx)
        if agent.y < self.ball.y:
            self.assertTrue(initial_speed_y < self.ball.vy)
        else:
            self.assertTrue(initial_speed_y > self.ball.vy)

    @parameterized.expand([
        [Agent(-1, WINDOW_WIDTH_ADULT_SIZE / 2 - 5, WINDOW_HEIGHT_ADULT_SIZE / 2, 10, 'red', 0,
               DefaultRelativeState())],
        [Agent(-1, WINDOW_WIDTH_ADULT_SIZE / 2, WINDOW_HEIGHT_ADULT_SIZE / 2 + 5, 10, 'red', 0,
               DefaultRelativeState())],
        [Agent(-1, WINDOW_WIDTH_ADULT_SIZE / 2 + 15, WINDOW_HEIGHT_ADULT_SIZE / 2 + 15, 10, 'red', 0,
               DefaultRelativeState())],

    ])
    def test_collision_with_player(self, agent):
        initial_position_x = self.ball.x
        initial_position_y = self.ball.y
        distance = sqrt(
            (self.ball.x - agent.x) * (self.ball.x - agent.x) + (self.ball.y - agent.y) * (self.ball.y - agent.y))
        radius_sum = self.ball.r + agent.r
        self.ball.collision_with_player(agent)

        if distance < radius_sum:
            self.assertTrue((initial_position_x != self.ball.x) or (initial_position_y != self.ball.y))
        else:
            self.assertEqual(initial_position_x, self.ball.x)
            self.assertEqual(initial_position_y, self.ball.y)
        return True

    @parameterized.expand([
        [FieldModel(AdultSizeFactory().create_field_specification()), 29, 22, True],
        [FieldModel(AdultSizeFactory().create_field_specification()), 0, 22, False],
    ])
    def test_collision_with_goal(self, field_model, initial_position_x, initial_position_y, is_placed_in_goal):
        self.ball.x = initial_position_x
        self.ball.y = initial_position_y

        self.ball.collision_with_goal(field_model)
        if is_placed_in_goal:
            self.assertTrue(initial_position_x != self.ball.x or initial_position_y != self.ball.y)
        else:
            self.assertTrue(initial_position_x == self.ball.x or initial_position_y == self.ball.y)
        return True

    @parameterized.expand([
        [10],
        [0],
    ])
    def test_update(self, speed):
        initial_position = self.ball.x
        self.ball.vx = speed
        self.ball.update(
            field_model=FieldModel(AdultSizeFactory().create_field_specification()))
        new_position = self.ball.x
        if speed != 0:
            self.assertNotEqual(initial_position, new_position, "Ball position expected to change")
        else:
            self.assertEqual(initial_position, new_position, "Ball position expected remain the same")

    @parameterized.expand([
        [Agent(-1, 2, 22, 1, 'red', 0, DefaultRelativeState())],
        [Agent(1, -2, 22, 1, 'red', 0, DefaultRelativeState())],
    ])
    def test_get_dist(self, p):
        distance_squared = (self.ball.x - p.x) * (self.ball.x - p.x) + (self.ball.y - p.y) * (self.ball.y - p.y)
        self.assertEqual(self.ball.get_dist(p), distance_squared)

    @parameterized.expand([
        [Agent(-1, 2, 22, 1, 'red', 0, DefaultRelativeState())],
        [Agent(1, -2, 22, 1, 'red', 0, DefaultRelativeState())],
        [Agent(1, 0.1, 22, 1, 'red', 0, DefaultRelativeState())],
    ])
    def test_is_colliding(self, p):
        if self.ball.get_dist(p) < (self.ball.r + p.r) * (self.ball.r + p.r):

            self.assertTrue(self.ball.is_colliding(p), "Ball expected to be in collision with agent")
        else:
            self.assertFalse(self.ball.is_colliding(p), "Ball not expected to be in collision with agent")


if __name__ == '__main__':
    unittest.main()
