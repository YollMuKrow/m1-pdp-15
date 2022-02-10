import unittest
from unittest.mock import Mock

import numpy as np

from slimevolleygym import RelativeState, Agent, Particle
from parameterized import parameterized

BALL_COLOR = (217, 79, 0)

REF_W = 24 * 2


class TestSequence(unittest.TestCase):
    @parameterized.expand([
        ["foo", "a", "a", ],
        ["bar", "a", "a"],
        ["lee", "a", "a"],
    ])
    def test_sequence(self, name, a, b):
        self.assertEqual(a, b)


class TestAgent(unittest.TestCase):

    def setUp(self) -> None:
        self.agent_team_left_1 = Agent(-1, - REF_W / 6, 1.5, 'purple')
        self.agent_team_left_2 = Agent(-1, -2 * REF_W / 6, 1.5, 'green')

        self.agent_team_right_1 = Agent(1, REF_W / 6, 1.5, 'yellow')
        self.agent_team_right_2 = Agent(1, 2 * REF_W / 6, 1.5, 'white')

        self.ball1 = Particle(REF_W / 6, 4, 8, 2, 0.5, BALL_COLOR)
        self.ball2 = Particle(- REF_W / 6, 4, -8, -2, 0.5, BALL_COLOR)

    # def test_update_self_state(self):
    #     self.agent_team_left_1.state = Mock()
    #
    #     self.agent_team_left_1._update_self_state()
    #
    #     x = self.agent_team_left_1.x * self.agent_team_left_1.dir
    #     y = self.agent_team_left_1.y
    #     vx = self.agent_team_left_1.vx * self.agent_team_left_1.dir
    #     vy = self.agent_team_right_2.vy
    #
    #     self.agent_team_left_1.state.set_agent_state.assert_called_once_with((x, y, vx, vy))


if __name__ == '__main__':
    unittest.main()
