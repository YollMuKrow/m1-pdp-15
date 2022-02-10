import unittest

from parameterized import parameterized

from robocup import AdultSizeGameBuilder
from robocup.creation.factory import AdultSizeFactory, KidSizeFactory
from robocup.dynamic_object.state import DefaultRelativeState
from robocup.spec.settings import *
from robocup.game import *
from robocup.dynamic_object.player import *
from lib import jsonLib


class TestGame(unittest.TestCase):

    def setUp(self) -> None:
        team_left_color_num_action_dict = {"yellow": 0, "green": 1}
        player_1 = Agent(1, 4, 20, 1, 'yellow', 0, DefaultRelativeState())
        player_2 = Agent(1, 4, 12, 1, 'green', 0, DefaultRelativeState())
        color_agent_dict = {"yellow": player_1, "green": player_2}
        team_left = Team("red", team_left_color_num_action_dict, color_agent_dict)

        team_left_color_num_action_dict = {"red": 2, "blue": 3}
        player_2 = Agent(-1, -4, 20, 1, 'red', 0, DefaultRelativeState())
        player_3 = Agent(-1, -4, 12, 1, 'blue', 0, DefaultRelativeState())
        color_agent_dict = {"red": player_2, "blue": player_3}
        team_right = Team("purple", team_left_color_num_action_dict, color_agent_dict)

        ball = Ball(0, 16, 1, BALL_COLOR)
        field_model = FieldModel(KidSizeFactory().create_field_specification())
        referee = Referee(team_left, team_right, field_model, ball)
        delay_screen = DelayScreen(0)

        self.game = Game(field_model, team_left, team_right, ball, referee, delay_screen, "yellow")

    def test_initialization(self):
        team_left_color_num_action_dict = {"yellow": 0, "green": 1}
        player_1 = Agent(-1, -2, 24, 1, 'yellow', 0, DefaultRelativeState())
        player_2 = Agent(-1, -2, 18, 1, 'green', 0, DefaultRelativeState())
        color_agent_dict = {"yellow": player_1, "green": player_2}
        team_left = Team("red", team_left_color_num_action_dict, color_agent_dict)

        team_right_color_num_action_dict = {"red": 2, "blue": 3}
        player_2 = Agent(1, 2, 24, 1, 'red', 0, DefaultRelativeState())
        player_3 = Agent(1, 2, 20, 1, 'blue', 0, DefaultRelativeState())
        color_agent_dict = {"red": player_2, "blue": player_3}
        team_right = Team("purple", team_right_color_num_action_dict, color_agent_dict)

        ball = Ball(0, 22, 1, BALL_COLOR)
        field_model = FieldModel(AdultSizeFactory().create_field_specification())
        referee = Referee(team_left, team_right, field_model, ball)
        delay_screen = DelayScreen(0)

        game = Game(field_model, team_right, team_right, ball, referee, delay_screen, "yellow")
        self.assertIsNotNone(game, "Game expected to exist")

    @parameterized.expand([
        [10, 24, 6, 5],
        [1, -2, 22, 1],
    ])
    def test_reset(self, n1, n2, n3, n4):
        return True
        self.game = self.game.reset()
        initial_agent_left_x = self.game.team_left.get_agent('green').x
        initial_agent_right_y = self.game.team_right.get_agent('red').y
        initial_agent_ball_vx = self.game.ball.vx
        initial_agent_referee_ball_r = self.game.referee.ball.r
        initial_points_left = self.game.team_left.points

        self.game.team_left.get_agent('green').vx = n1
        self.game.team_right.get_agent('red').vy = n2
        self.game.ball.vx = n3
        self.game.referee.ball.r = n4
        self.game.team_left.points += 1

        self.game.step()
        self.game = self.game.reset()

        self.assertEqual(initial_agent_left_x, self.game.team_left.get_agent('green').x)
        self.assertEqual(initial_agent_right_y, self.game.team_right.get_agent('red').y)
        self.assertEqual(round(initial_agent_ball_vx), round(self.game.ball.vx))
        #self.assertEqual(initial_agent_referee_ball_r, self.game.referee.ball.r)
        #self.assertEqual(initial_points_left, self.game.team_left.points)

    @parameterized.expand([
        [1, 4, 3, 2],
        [1, -2, 2, 1],
    ])
    def test_new_match(self, n1, n2, n3, n4):
        print("debug: ", self.game.team_left.get_agent('green'))
        initial_agent_left_x = self.game.team_left.get_agent('green').x
        initial_agent_agent_right_y = self.game.team_right.get_agent('red').y
        initial_agent_ball_vx = self.game.ball.vx
        initial_points_left = self.game.team_left.points

        self.game.team_left.get_agent('green').x += n1
        self.game.team_right.get_agent('red').y += n2
        self.game.ball.vx = n3
        self.game.team_left.points += n4

        self.game.new_match()
        self.assertEqual(initial_agent_left_x, self.game.team_left.get_agent('green').x)
        self.assertEqual(initial_agent_agent_right_y, self.game.team_right.get_agent('red').y)
        self.assertEqual(initial_agent_ball_vx, self.game.ball.vx)
        self.assertNotEqual(initial_points_left, self.game.team_left.points)

    @parameterized.expand([
        [2, 3],
        [1, -2],
    ])
    def test_step(self, vx, vy):
        initial_agent_left_x = self.game.team_left.get_agent('green').x
        initial_agent_left_vy = self.game.team_left.get_agent('green').vy
        initial_ball_x = self.game.ball.x
        initial_ball_y = self.game.ball.y

        self.game.team_left.get_agent('green').desired_vx = vx
        self.game.team_left.get_agent('green').desired_vy = vy
        self.game.ball.vx = vx
        self.game.ball.vy = vy
        self.game.step()

        if vx != 0:
            self.assertNotEqual(initial_agent_left_x, self.game.team_left.get_agent('green').x)
            self.assertNotEqual(initial_ball_x, self.game.ball.x)
        if vy != 0:
            self.assertNotEqual(initial_agent_left_vy, self.game.team_left.get_agent('green').vy)
            self.assertNotEqual(initial_ball_y, self.game.ball.y)

        self.game.reset()

        initial_ball_x = self.game.ball.x
        initial_ball_y = self.game.ball.y

        # put the agent on the ball to force collision
        self.game.team_left.get_agent('green').x = 0.1

        self.game.step()
        self.game.step()

        self.assertTrue(initial_ball_x != self.game.ball.x or initial_ball_y != self.game.ball.y)

        self.game.reset()

        initial_points_left = self.game.team_left.points
        initial_points_right = self.game.team_right.points

        # put the ball in the goal
        self.game.ball.x = self.game.field_model.goal_data.get("goal_right_x")
        self.game.ball.y = (self.game.field_model.goal_data.get("goal_y")+self.game.field_model.goal_data.get("goal_height")/2)/2
        self.game.step()
        self.assertTrue(
            (initial_points_left != self.game.team_left.points) or (initial_points_right != self.game.team_right.points))

    def test_get_agent_being_trained_observation(self):
        self.assertIsNotNone(self.game.get_agent_being_trained_observation())

    def test_get_other_observation(self):
        self.assertIsNotNone(self.game.get_other_observation())
