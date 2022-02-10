from unittest import TestCase

from parameterized import parameterized

from robocup import AdultSizeGameBuilder, GameBuilder
from robocup.creation.factory import AdultSizeFactory
from robocup.dynamic_object.state import *
from robocup.dynamic_object.team import *
from robocup.rules.field import *
from lib import jsonLib
from robocup.spec.settings import BALL_COLOR


class TestTeam(TestCase):
    def setUp(self) -> None:
        team_left_color_num_action_dict = {"yellow": 0, "green": 1}
        player_1 = Agent(1, -2, 22, 1, 'yellow', 0, DefaultRelativeState())
        player_2 = Agent(1, 2, 22, 1, 'green', 0, DefaultRelativeState())
        color_agent_dict = {"yellow": player_1, "green": player_2}
        self.team = Team("red", team_left_color_num_action_dict, color_agent_dict)

    def test_initialization(self):
        team_left_color_num_action_dict = {"yellow": 0, "green": 1}
        player_1 = Agent(1, 2, 24, 1, 'yellow', 0, DefaultRelativeState())
        player_2 = Agent(1, 2, 20, 1, 'green', 0, DefaultRelativeState())
        color_agent_dict = {"yellow": player_1, "green": player_2}
        team_1 = Team("red", team_left_color_num_action_dict, color_agent_dict)
        self.assertIsNotNone(team_1)

    @parameterized.expand([
        [[0, 0, 0, 0, 0, 0, 0]],
    ])
    def test_set_action(self, action_list):
        for color_agent, num_action in self.team.color_num_action_dict.items():
            agent = self.team.color_agent_dict[color_agent]
            agent.desired_vx = 9

        self.team.set_actions(action_list)

        for color_agent, num_action in self.team.color_num_action_dict.items():
            agent = self.team.color_agent_dict[color_agent]
            self.assertEqual(agent.desired_vx, 0, "Speed expected to be set to 0 with action being set to nothing")

    @parameterized.expand([
        [FieldModel(AdultSizeFactory().create_field_specification()), 5],
        [FieldModel(AdultSizeFactory().create_field_specification()), 0],
    ])
    def test_update(self, field_model, noise):
        agent = self.team.color_agent_dict['green']
        initial_x = agent.x
        agent.desired_vx = noise
        self.team.update(field_model)
        updated_x = agent.x
        if noise != 0:
            self.assertNotEqual(initial_x, updated_x)
        else:
            self.assertEqual(initial_x, updated_x)

    @parameterized.expand([
        [FieldModel(AdultSizeFactory().create_field_specification()), 5],
        [FieldModel(AdultSizeFactory().create_field_specification()), 0],
    ])
    def test_update_state(self, field_model, noise):
        ball = Ball(0, 22, 1, BALL_COLOR)
        team_left_color_num_action_dict = {"red": 2, "blue": 3}
        player_2 = Agent(-1, -2, 24, 1, 'red', 0, DefaultRelativeState())
        player_3 = Agent(-1, -2, 20, 1, 'blue', 0, DefaultRelativeState())
        color_agent_dict = {"red": player_2, "blue": player_3}
        team_2 = Team("purple", team_left_color_num_action_dict, color_agent_dict)
        agent = self.team.color_agent_dict['green']

        self.team.update(field_model)
        agent.update_state(ball, self.team.color_agent_dict, team_2.color_agent_dict)
        initial_state = agent.state.get_observation()

        agent.x += noise
        ball.x += noise

        self.team.update_state(ball, team_2.color_agent_dict)

        if noise != 0:
            self.assertNotEqual(initial_state[0], agent.state.get_observation()[0])
            self.assertNotEqual(initial_state[4], agent.state.get_observation()[4])

        else:
            for i in range(len(initial_state)):
                self.assertEqual(initial_state[i], agent.state.get_observation()[i])

    @parameterized.expand([
        ['green'],
        ['yellow'],
    ])
    def test_get_agent(self, color_agent):
        self.assertIsNotNone(self.team.get_agent(color_agent))

    @parameterized.expand([
        [10], [0],
    ])
    def test_reset_position(self, noise):
        player_1 = self.team.color_agent_dict['green']
        player_2 = self.team.color_agent_dict['yellow']
        initial_x_1 = player_1.x
        initial_x_2 = player_2.x
        player_1.x += noise
        player_2.x += noise
        self.team.reset_position()
        self.assertEqual(initial_x_1, player_1.x)
        self.assertEqual(initial_x_2, player_2.x)

    def test_reset_position_after_mid_game(self):
        player_1 = self.team.color_agent_dict['green']
        player_2 = self.team.color_agent_dict['yellow']
        initial_x_1 = player_1.x
        initial_x_2 = player_2.x

        self.team.reset_position_after_mid_game()
        self.assertNotEqual(initial_x_1, player_1.x)
        self.assertNotEqual(initial_x_2, player_2.x)

    @parameterized.expand([
        [Ball(0, 22, 1, BALL_COLOR)],
    ])
    def test_manage_interaction_with_ball(self, ball):
        initial_touch = self.team.manage_interaction_with_ball(ball)
        player_1 = self.team.color_agent_dict['green']
        player_1.x = ball.x + player_1.r / 2
        new_touch = self.team.manage_interaction_with_ball(ball)
        self.assertNotEqual(initial_touch, new_touch)

    def test_get_observation(self):
        self.assertIsNotNone(self.team.get_observation)
