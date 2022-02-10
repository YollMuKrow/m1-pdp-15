import unittest

from parameterized import parameterized

from robocup.dynamic_object.ball import Ball
from robocup.dynamic_object.state import *
from robocup.rules.field import FieldModel
from robocup.dynamic_object.player import Agent
from robocup.spec.settings import *
from robocup.creation.factory import AdultSizeFactory, KidSizeFactory


class TestAgent(unittest.TestCase):

    def setUp(self) -> None:
        self.agent = Agent(1, 0, 22, 1, 'red', 0, DefaultRelativeState())

    @parameterized.expand([
        [-1, 2, 22, 1, 'green', 0],
        [1, -2, 22, 1, 'red', 0],
    ])
    def test_initialization(self, expected_dir, expected_x, expected_y, expected_r, expected_c, expected_a):
        agent1 = Agent(expected_dir, expected_x, expected_y, expected_r, expected_c, expected_a, DefaultRelativeState())
        self.assertIsNotNone(agent1, "Agent initialized")

    @parameterized.expand([
        [10, 10],
        [1, -2],
    ])
    def test_reset_position(self, x, y):
        self.agent.x = x
        self.agent.y = y
        self.agent.reset_position()
        self.assertEqual(self.agent.x, self.agent.init_x, "Position expected to be reset to initial position")
        self.assertEqual(self.agent.y, self.agent.init_y, "Position expected to be reset to initial position")

    @parameterized.expand([
        [10, 10],
        [1, -2],
        [5312, -7934]
    ])
    def test_reset_position_after_mid_game(self, x, y):
        self.agent.x = x
        self.agent.y = y
        direction = self.agent.dir
        self.agent.reset_position_after_mid_game()
        self.assertEqual(direction, -self.agent.dir, "Direction expected to be reset")
        self.assertEqual(self.agent.x, -self.agent.init_x, "Pos x expected to be reset")
        self.assertEqual(self.agent.y, self.agent.init_y, "Pos y expected to be reset")

    @parameterized.expand([
        [[1, 0, 0, 0, 0, 0, 0]],
        [[0, 1, 0, 0, 0, 0, 0]],
        [[0, 0, 1, 0, 0, 0, 0]],
        [[0, 0, 0, 1, 0, 0, 0]],
    ])
    def test_set_action(self, action):
        self.agent.set_action(action)
        if action[0] > 0 and action[1] == 0:
            self.assertEqual(self.agent.desired_vx, PLAYER_SPEED_LEFT, "Agent desired speed expected to be set")
        if action[1] > 0 and action[0] == 0:
            self.assertEqual(self.agent.desired_vx, -PLAYER_SPEED_RIGHT, "Agent desired speed expected to be set")
        if action[2] > 0 and action[3] == 0:
            self.assertEqual(self.agent.desired_vy, PLAYER_SPEED_FORWARD, "Agent desired speed expected to be set")
        if action[3] > 0 and action[2] == 0:
            self.assertEqual(self.agent.desired_vy, -PLAYER_SPEED_BACKWARD, "Agent desired speed expected to be set")
        return True

    @parameterized.expand([
        [1],
        [0],
    ])
    def test_move(self, speed):
        initial_position = self.agent.x
        self.agent.vx = speed
        self.agent.move()
        new_position = self.agent.x
        if speed != 0:
            self.assertNotEqual(initial_position, new_position, "Agent position expected to change")
        else:
            self.assertEqual(initial_position, new_position, "Agent position expected not to change")

    @parameterized.expand([
        [10, 10, 0, 0, 90, -10, 10],
        [5, 0, 0, 0, 90, 0, 5],
        [5, 0, 0, 0, 180, -5, 0]
    ])
    def test_rotate(self, x, y, x0, y0, angle, rot_x, rot_y):
        self.agent.x = x0
        self.agent.y = y0
        self.agent.point_circle_hitbox.x = x
        self.agent.point_circle_hitbox.y = y
        self.agent.desired_angle = angle
        self.agent.rotate()
        self.assertEqual(
            (round(self.agent.point_circle_hitbox.x), round(self.agent.point_circle_hitbox.y)),
            (rot_x, rot_y)
        )

    @parameterized.expand([
        [10, 10, 0, 10, 10, (20, 10)],
        [15, 30, 90, 20, 20, (15, 50)],
        [10, 10, 0, 0, 0, (10, 10)]
    ])
    def test_next_position(self, x, y, angle, vx, vy, must_be_equal):
        self.agent.desired_vx = vx / TIMESTEP
        self.agent.desired_vy = vy / TIMESTEP
        self.agent.origin_angle = angle
        self.agent.x = x
        self.agent.y = y
        nxtp = self.agent.next_position()
        self.assertEqual(
            must_be_equal,
            (round(nxtp.x), round(nxtp.y)),
            "Next position according calculated with the speed and angle")

    @parameterized.expand([
        [0., 64., -4.0, 18.0],
        [-32, 44, 1, 2]
    ])
    def test_is_outside_field(self, posOutsideX, posOutsideY, posInsideX, posInsideY):
        fm = FieldModel(KidSizeFactory().create_field_specification())
        self.agent.r = 0.1
        self.assertTrue(self.agent.is_outside_field(posOutsideX,
                                                    posOutsideY,
                                                    fm))
        self.assertFalse(self.agent.is_outside_field(posInsideX,
                                                     posInsideY,
                                                     fm))

    @parameterized.expand([
        [4234235, 3125],
        [-84385, -209409075]
    ])
    def test_cancel_movement(self, vx, vy):
        self.agent.desired_vx = vx
        self.agent.desired_vy = vy
        self.agent.cancel_movement()
        self.assertEqual(self.agent.desired_vx, 0)
        self.assertEqual(self.agent.desired_vy, 0)

    @parameterized.expand([
        [19, -78, 0, 0],
        [1, 2, 0, 0],
        [0, 0, 0, 0]
    ])
    def test_update(self, vx, vy, x, y):
        fm = FieldModel(KidSizeFactory().create_field_specification())
        self.agent.desired_vx = vx
        self.agent.desired_vy = vy
        self.agent.x = x
        self.agent.y = y
        self.agent.update(fm)
        if x == 0 or y == 0:
            self.assertEqual(self.agent.y, 0, "Position has been updated")
            self.assertEqual(self.agent.y, 0, "Position has been updated")
        else:
            self.assertNotEqual(self.agent.x, 0, "Position hasn't been updated")
            self.assertNotEqual(self.agent.y, 0, "Position hasn't been updated")

    @parameterized.expand([
        [FieldModel(KidSizeFactory().create_field_specification()), 0, 16, 0.5, 15.5, 0.8]
    ])
    def test_manage_shot_rotated(self, fm, ball_x0, ball_y0, ready_to_shot_x, ready_to_shot_y, radius):
        ball = Ball(ball_x0, ball_y0, 1, BALL_COLOR)
        self.agent.point_circle_hitbox.x = ready_to_shot_x
        self.agent.point_circle_hitbox.y = ready_to_shot_y
        self.agent.r = radius
        self.agent.is_shooting = True
        a = self.agent.manage_shot_rotated(ball)
        ball.update(fm)
        self.assertNotEqual((ball.x, ball.y),
                            (ball_x0, ball_y0))
        self.assertTrue(a)


if __name__ == '__main__':
    unittest.main()
