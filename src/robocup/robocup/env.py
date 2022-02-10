from typing import List, Dict, Optional

import gym
from gym import spaces, Space
from gym.envs.classic_control.rendering import Viewer
from gym.utils import seeding
from gym.envs.registration import register
from time import time
from gym.envs.classic_control import rendering as rendering

import numpy as np
from numpy import ndarray

from robocup.creation.builder import AdultSizeGameBuilder, GameDirector, GameBuilder, KidSizeGameBuilder
from robocup.spec.settings import WINDOW_WIDTH_ADULT_SIZE, WINDOW_HEIGHT_ADULT_SIZE, WINDOW_WIDTH_KID_SIZE, \
    WINDOW_HEIGHT_KID_SIZE, MATCH_MAX_TIME, MATCH_MID_TIME
from robocup.game import Game
from robocup.utility.func_utility import check_if_duplicate
from robocup.view.view import *

np.set_printoptions(threshold=20, precision=3, suppress=True, linewidth=200)


# Classe permettant de générer des actions aléatoire pour tester l'implémentation de l'environnement
class RandomPolicy:
    def __init__(self):
        self.action_space: Space = gym.spaces.MultiBinary(7)
        pass

    #   Permet de simuler une prédiction d'action
    #   Paramètres :
    #   ------------
    #   None
    #
    #   Sorties
    #   -------
    #   Space
    #       Tableau d'action comprennat des valeurs aléatoire (0 ou 1)
    def predict(self) -> Space:
        return self.action_space.sample()


# Classe définissant l'environnement dans lequel vont apprendre les agents
class RoboCupEnv(gym.Env):
    metadata = {
        'render.modes': ['human', 'rgb_array', 'state'],
        'video.frames_per_second': 50

    }

    def __init__(self, game: Game, window_width: int, window_height: int, observation_space_length: int = 20):

        self.mid_game_event = False
        self.game: Game = game

        self.team_left_color_num_action_dict: Dict[str, int] = self.game.team_left.color_num_action_dict
        self.team_right_color_num_action_dict: Dict[str, int] = self.game.team_right.color_num_action_dict

        self._verify_team()
        self.start_time = time()

        self.t_mid_game_limit = MATCH_MID_TIME
        self.t_end_game = MATCH_MAX_TIME

        self.action_space: Space = spaces.MultiBinary(7)

        high = np.array([np.finfo(np.float32).max] * observation_space_length)
        self.observation_space: Space = spaces.Box(-high, high)

        self.viewer: Viewer = None

        self.view: View = View(window_width=window_width, window_height=window_height,
                               field_model=self.game.field_model, team_left=self.game.team_left,
                               team_right=self.game.team_right, ball=self.game.ball)

    # Vérifie que chaque équipe est dans le bon format et comprend le bon nombre de joueur
    #
    #   Paramètres :
    #   ------------
    #   None
    #
    #   Sorties
    #   -------
    #   None
    def _verify_team(self) -> None:

        both_team_list = [*self.team_left_color_num_action_dict.values(),
                          *self.team_right_color_num_action_dict.values()]

        filtered = filter(lambda num_action: num_action < 0 or num_action >= 4, both_team_list)

        list_filtered = list(filtered)

        assert len(list_filtered) == 0
        assert check_if_duplicate(both_team_list) == False

    # Retourne la graine aléatoire servant à générer la partie
    #
    #   Paramètres :
    #   ------------
    #   seed: int
    #       graine aléatoire choisit par l'utilisateur
    #   Sorties
    #   -------
    #   seed :[int]
    def seed(self, seed=None) -> None:
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    # Récupère l'espace d'observation de l'agent qu'on entraine
    #
    #   Paramètres :
    #   ------------
    #   None
    #
    #   Sorties
    #   -------
    #   ndarray
    #       la matrice d'observation par état de l'agent entrainé
    def _get_observation(self) -> ndarray:

        obs = self.game.get_agent_being_trained_observation()
        return obs

    # Boucle de jeu de l'environnement
    #
    #   Paramètres :
    #   ------------
    #   action: List[int]
    #       liste d'action effectué par les agents
    #   *args
    #       Suite de la liste d'action effectué par les agents
    #
    #   Sorties
    #   -------
    #   Tuple[ndarray, int, bool, Dict[str, Optional[int]]]
    #       retourne l'observation, la récompense, l'état du jeu(fini ou pas) et la liste d'information sur l'état
    #       de la partie
    def step(self, action: List[int], *args) -> Tuple[ndarray, int, bool, Dict[str, Optional[int]]]:

        done = False

        assert len(args) <= 4 - 1

        self.game.team_left.set_actions(action, *args)
        self.game.team_right.set_actions(action, *args)

        reward = self.game.step()

        obs = self._get_observation()

        local_t = time()
        time_difference = local_t - self.start_time
        if self.t_mid_game_limit < time_difference and not self.mid_game_event:
            self.game.mid_game_event()
            self.mid_game_event = True
            print("mid game status")

        if self.game.team_left.points >= 5 or self.game.team_right.points >= 5 or self.t_end_game < time_difference:
            print("Fin du match !")
            done = True

        info = {
            'team_left_points': self.game.team_left.points,
            'team_right_points': self.game.team_right.points,
        }

        other_obs = self.game.get_other_observation()

        info.update(other_obs)

        return obs, reward, done, info

    # Génère l'objet game dans son état vierge
    #
    #   Paramètres :
    #   ------------
    #   None
    #
    #   Sorties
    #   -------
    #   None
    def _init_game_state(self) -> None:
        self.game = self.game.reset()

    # Remet à zéro la partie
    #
    #   Paramètres :
    #   ------------
    #   None
    #
    #   Sorties
    #   -------
    #   ndarray
    #       la matrice d'observation par défaut du jeu
    def reset(self) -> ndarray:
        self._init_game_state()
        return self._get_observation()

    # Gère l'affichage de la fenêtre avec la bibliothèque gym
    #
    #   Paramètres :
    #   ------------
    #   None
    #
    #   Sorties
    #   -------
    #   None
    def render(self, mode='human', close=False) -> None:

        if self.viewer is None:
            self.viewer = rendering.Viewer(self.view.window.window_width, self.view.window.window_height)

        self.view.update_view(field_model=self.game.field_model, team_left=self.game.team_left,
                              team_right=self.game.team_right, ball=self.game.ball)
        self.view.display(self.viewer)
        return self.viewer.render(return_rgb_array=mode == 'rgb_array')

    # Gère la fermeture de la fenêtre avec la bibliothèque gym
    #
    #   Paramètres :
    #   ------------
    #   None
    #
    #   Sorties
    #   -------
    #   None
    def close(self) -> None:
        if self.viewer:
            self.viewer.close()

    # Gère le champ de vision des agents en soustrayant certaines données d'observation pour simuler un champ de vision
    #
    #   Paramètres :
    #   ------------
    #   configuration: List[str]
    #
    #
    #   Sorties
    #   -------
    #   int
    #       la taille de la matrice d'observation


def length_observation_space(configuration: List[str]) -> int:
    length = 20
    if configuration.__contains__('allies_vision_disable') and configuration.__contains__('opponents_vision_disable'):
        length = 8
    elif configuration.__contains__('allies_vision_disable'):
        length = 16
    elif configuration.__contains__('opponents_vision_disable'):
        length = 12

    return length

    # Créer l'environnement AdultSize pour la robocup
    #
    #   Paramètres :
    #   ------------
    #   None
    #
    #   Sorties
    #   -------
    #   None
    #


class AdultSizeEnv(RoboCupEnv):

    def __init__(self, team_left_color_num_action_dict: Dict[str, int],
                 team_right_color_num_action_dict: Dict[str, int], configuration: List[str]):
        adult_size_game_builder: AdultSizeGameBuilder = AdultSizeGameBuilder()
        game_director: GameDirector = GameDirector(
            team_left_color_num_action_dict=team_left_color_num_action_dict,
            team_right_color_num_action_dict=team_right_color_num_action_dict)

        game_director.builder = adult_size_game_builder
        game_director.start_build(build_configuration=configuration)
        game = adult_size_game_builder.game

        observation_space_length = length_observation_space(configuration=configuration)

        print(observation_space_length)

        super().__init__(game=game,
                         window_width=WINDOW_WIDTH_ADULT_SIZE,
                         window_height=WINDOW_HEIGHT_ADULT_SIZE, observation_space_length=observation_space_length)

    # Créer l'environnement KidSize pour la robocup
    #
    #   Paramètres :
    #   ------------
    #   None
    #
    #   Sorties
    #   -------
    #   None
    #


class KidSizeEnv(RoboCupEnv):

    def __init__(self, team_left_color_num_action_dict: Dict[str, int],
                 team_right_color_num_action_dict: Dict[str, int], configuration: List[str]):
        kid_size_game_builder: KidSizeGameBuilder = KidSizeGameBuilder()
        game_director: GameDirector = GameDirector(
            team_left_color_num_action_dict=team_left_color_num_action_dict,
            team_right_color_num_action_dict=team_right_color_num_action_dict)

        game_director.builder = kid_size_game_builder
        game_director.start_build(build_configuration=configuration)
        game = kid_size_game_builder.game

        observation_space_length = length_observation_space(configuration=configuration)

        super().__init__(game=game,
                         window_width=WINDOW_WIDTH_KID_SIZE,
                         window_height=WINDOW_HEIGHT_KID_SIZE, observation_space_length=observation_space_length)

        pass


####################
# Reg envs for gym #
####################

register(
    id='RoboCupAdultSize-v0',
    entry_point='robocup:AdultSizeEnv',
    kwargs={'team_left_color_num_action_dict': {'purple': 0, 'green': 1}, 'team_right_color_num_action_dict':
        {'yellow': 2, 'white': 3}, 'configuration': []}
)

register(
    id='RoboCupKidSize-v0',
    entry_point='robocup:KidSizeEnv',
    kwargs={'team_left_color_num_action_dict': {'purple': 0, 'green': 1}, 'team_right_color_num_action_dict':
        {'yellow': 2, 'white': 3}, 'configuration': []}
)
