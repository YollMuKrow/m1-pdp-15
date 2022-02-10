from abc import abstractmethod
from typing import List

import numpy as np

from numpy import ndarray


# Interface, défini les traitements

class RelativeState:

    # Utiliser pour mettre à jour les données d'état de l'agent pour lequel on construit l'espace d'observations (coordonnées, vitesse)
    #
    #     Paramètres
    #     ----------
    #     agent: Agent
    #           on récupère les coordonnées, vitesse x y de cet agent
    #     Sorties
    #     -------

    @abstractmethod
    def update_self_state(self, agent) -> None:
        pass

    # Utiliser pour mettre à jour les données d'état de la balle par rapport à l'agent pour lequel on construit l'espace d'observations (coordonnées, vitesse)
    #
    #     Paramètres
    #     ----------
    #     agent: Agent
    #           on récupère les coordonnées, vitesse x y de cet agent
    #     ball: Ball
    #           on récupère les coordonnées, vitesse x y de la balle
    #     Sorties
    #     -------

    @abstractmethod
    def update_ball_state(self, agent, ball) -> None:
        pass

    # Utiliser pour mettre à jour les données d'état des alliés par rapport à l'agent pour lequel on construit l'espace d'observations (coordonnées, vitesse)
    #
    #     Paramètres
    #     ----------
    #     agent: Agent
    #           on récupère les coordonnées, vitesse x y de cet agent
    #     allies_dict: Dict[str, Agent]
    #           on récupère les coordonnées, vitesse x y de des alliés de l'agent
    #     Sorties
    #     -------

    @abstractmethod
    def update_allies_state(self, agent=None, allies_dict=None) -> None:
        pass

    # Utiliser pour mettre à jour les données d'état des opposants par rapport à l'agent pour lequel on construit l'espace d'observations (coordonnées, vitesse)
    #
    #     Paramètres
    #     ----------
    #     agent: Agent
    #           on récupère les coordonnées, vitesse x y de cet agent
    #     opponents_dict: Dict[str, Agent]
    #           on récupère les coordonnées, vitesse x y de des opposants de l'agent
    #     Sorties
    #     -------

    @abstractmethod
    def update_opponents_state(self, agent=None, opponents_dict=None) -> None:
        pass

    # Réinitialise la matrice d'observation par états
    #
    #     Paramètres
    #     ----------
    #     Sorties
    #     -------

    @abstractmethod
    def reset_state_observation_matrix(self) -> None:
        pass

    # Met à jour la matrice d'observation par états d'un agent
    #
    #     Paramètres
    #     ----------
    #     state_observation_list: List[float]):
    #           liste qui contient [x, y, vx, vy]
    #     Sorties
    #     -------
    #

    @abstractmethod
    def update_state_observation_matrix(self, state_observation_list: List[float]):
        pass

    # Retourne la matrice d'observation par états
    #
    #     Paramètres
    #     ----------
    #     Sorties
    #     -------
    #     ndarray
    #           la matrice d'observation par états d'un agent
    #

    @abstractmethod
    def get_observation(self) -> ndarray:
        pass

    # Classe utilisée pour représenter un composant concret DefaultRelativeState
    # Représente les données d'observation d'un agent donné
    #
    # Attributs
    # ----------
    # _x : float
    #     coordonnées x de l'agent pour lequel on construit l'espace d'observations
    # _y : float
    #     coordonnées y de l'agent pour lequel on construit l'espace d'observations
    # _vx : float
    #     vitesse x de l'agent pour lequel on construit l'espace d'observations
    # _vy : float
    #     vitesse y de l'agent pour lequel on construit l'espace d'observations
    # _bx : float
    #     coordonnées x de la balle
    # _by : float
    #     coordonnées y de la balle
    # _bvx : float
    #     vitesse x de la balle
    # _bvy: float
    #     vitesse y de la balle


class DefaultRelativeState(RelativeState):
    """
    keeps track of the obs.
    Note: the observation is from the perspective of the agent.
    an agent playing either side of the fence must see obs the same way
    """

    def __init__(self):
        # agent
        self._x: float = 0
        self._y: float = 0
        self._vx: float = 0
        self._vy: float = 0
        # ball

        self._bx: float = 0
        self._by: float = 0
        self._bvx: float = 0
        self._bvy: float = 0

        # la matrice est représentée sous forme d'une array numpy

        self._state_observation_matrix: ndarray = np.array([])

    def update_self_state(self, agent) -> None:
        self._x = agent.x * agent.dir
        self._y = agent.y
        self._vx = agent.vx * agent.dir
        self._vy = agent.vy

        self_state = [self._x, self._y, self._vx, self._vy]

        self._state_observation_matrix = np.append(self._state_observation_matrix, self_state)

    def update_ball_state(self, agent, ball) -> None:
        self._bx = ball.x * agent.dir
        self._by = ball.y
        self._bvx = ball.vx * agent.dir
        self._bvy = ball.vy

        ball_state = [self._bx, self._by, self._bvx, self._bvy]

        self._state_observation_matrix = np.append(self._state_observation_matrix, ball_state)

    # on ne définie pas cette méthode ici, on laisse les décorateurs le faire

    def update_allies_state(self, agent=None, allies_dict=None) -> None:
        pass

    def update_opponents_state(self, agent=None, opponents_dict=None) -> None:
        pass

    def reset_state_observation_matrix(self) -> None:
        self._state_observation_matrix: ndarray = np.array([])

    def update_state_observation_matrix(self, state_observation_list: List[float]):
        self._state_observation_matrix = np.append(self._state_observation_matrix, state_observation_list)

    def get_observation(self) -> ndarray:
        scale_factor = 10.0  # scale inputs to be in the order of magnitude of 10 for neural network.
        result = np.array(self._state_observation_matrix) / scale_factor
        return result


# Pattern décorateur (Decorator) pour gagner en souplesse

class RelativeStateDecorator(RelativeState):
    _relative_state: RelativeState

    def __init__(self, relative_state: RelativeState):
        self._relative_state = relative_state

    # les méthodes font appel au délégué

    def relative_state(self) -> RelativeState:
        return self._relative_state

    def update_self_state(self, agent) -> None:
        self._relative_state.update_self_state(agent=agent)

    def update_ball_state(self, agent, ball) -> None:
        self._relative_state.update_ball_state(agent=agent, ball=ball)

    def update_allies_state(self, agent=None, allies_dict=None) -> None:
        self._relative_state.update_allies_state(agent=agent, allies_dict=allies_dict)

    def update_opponents_state(self, agent=None, opponents_dict=None) -> None:
        self._relative_state.update_opponents_state(agent=agent, opponents_dict=opponents_dict)

    def reset_state_observation_matrix(self) -> None:
        self._relative_state.reset_state_observation_matrix()

    def update_state_observation_matrix(self, state_observation_list: List[float]):
        self._relative_state.update_state_observation_matrix(state_observation_list=state_observation_list)

    def get_observation(self) -> ndarray:
        return self._relative_state.get_observation()


# décorateur pour rajouter la vision des opposants

class OpponentsVision(RelativeStateDecorator):
    def update_opponents_state(self, agent=None, opponents_dict=None) -> None:
        for opponent_color, opponent in opponents_dict.items():
            opponent_x = opponent.x * (-agent.dir)
            opponent_y = opponent.y
            opponent_vx = opponent.vx * (-agent.dir)
            opponent_vy = opponent.vy

            opponent_state = [opponent_x, opponent_y, opponent_vx, opponent_vy]

            super().update_state_observation_matrix(state_observation_list=opponent_state)


# décorateur pour rajouter la vision des alliés

class AlliesVision(RelativeStateDecorator):
    def update_allies_state(self, agent=None, allies_dict=None) -> None:
        for ally_color, ally in allies_dict.items():
            ally_x = ally.x * agent.dir
            ally_y = ally.y
            ally_vx = ally.vx * agent.dir
            ally_vy = ally.vy

            ally_state = [ally_x, ally_y, ally_vx, ally_vy]

            super().update_state_observation_matrix(state_observation_list=ally_state)
