import unittest
from unittest.mock import Mock
import numpy as np

from slimevolleygym import RelativeState, Agent, Particle, Team, math
from parameterized import parameterized

BALL_COLOR = (217, 79, 0)

REF_W = 24 * 2


class TestTeam(unittest.TestCase):

    def setUp(self) -> None:
        self.team_left_dict = {'purple': 0, 'green': 1}
        self.team_right_dict = {'yellow': 2, 'white': 3}

        self.team_left: Team = Team('blue', -1, 2, self.team_left_dict)
        self.team_right: Team = Team('red', 1, 2, self.team_right_dict)

        self.agent_team_left_1 = Agent(-1, - REF_W / 6, 1.5, 'purple')
        self.agent_team_left_2 = Agent(-1, -2 * REF_W / 6, 1.5, 'green')

        self.agent_team_right_1 = Agent(1, REF_W / 6, 1.5, 'yellow')
        self.agent_team_right_2 = Agent(1, 2 * REF_W / 6, 1.5, 'white')

        self.ball1 = Particle(REF_W / 6, 4, 8, 2, 0.5, BALL_COLOR)
        self.ball2 = Particle(- REF_W / 6, 4, -8, -2, 0.5, BALL_COLOR)
    def __eqAgent__(self, agent1, agent2):
        return agent1.x == agent2.x and agent1.dir == agent2.dir and agent1.y == agent2.y and agent1.r == agent2.r and agent1.color_agent == agent2.color_agent and agent1.vx == agent2.vx and agent1.vy == agent2.vy
    def __eqTeam__(self, team1, team2):
        return team1.color_team == team2.color_team and team1.dir == team2.dir and team1.n == team2.n and team1.color_num_action_agent_dict == team2.color_num_action_agent_dict #and team1.agent_dict == team2.agent_dict

    #Nous testons la création de chaque élément d'une équipe lors de la création d'une équipe
    def testTeamCreationRight(self):
        team_right_test = Team('red', 1, 2, self.team_right_dict)
        assert self.__eqTeam__(team_right_test, self.team_right)

    def testTeamCreationLeft(self):
        team_left_test = Team('blue', -1, 2, self.team_left_dict)
        assert self.__eqTeam__(team_left_test, self.team_left)

    def testGetAgent(self):
        team_left_test = Team('red', -1, 2, self.team_left_dict)
        assert self.__eqAgent__(team_left_test.get_agent('purple'), self.agent_team_left_1) and self.__eqAgent__(team_left_test.get_agent('green'), self.agent_team_left_2)

    def testGetDistBetweenTeamMates(self):
        agent_list = [*self.team_left.agent_dict.values()]
        assert self.team_left.getDistBetweenTeamMates(self.agent_team_left_1, self.agent_team_left_2) == 8

    def testGetDistLeftAgent(self):
        agent_1 = Agent(-1, 10.5, 0.5, 'purple')
        agent_2 = Agent(-1, 10, 0, 'green')
        assert self.team_left.getDistLeftAgent(agent_1, agent_2) == math.sqrt(8)

    def testGetDistRightAgent(self):
        agent_1 = Agent(-1, 10.5, 0.5, 'purple')
        agent_2 = Agent(-1, 10, 0, 'green')
        assert self.team_left.getDistRightAgent(agent_1, agent_2) == math.sqrt(2)

    def testIsCollisionBetweenTeamMates(self):
        self.team_left.get_agent('green').x = 0
        self.team_left.get_agent('green').y = 0

        self.team_left.get_agent('purple').x = 0
        self.team_left.get_agent('purple').y = 0
        assert self.team_right.isCollisionBetweenTeamMates() == False and self.team_left.isCollisionBetweenTeamMates() == True


    # def testDisplay_team(self):
    #     return False


if __name__ == '__main__':
    unittest.main()
