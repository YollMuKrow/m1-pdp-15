
from typing import Dict

from robocup.dynamic_object.ball import Ball
from robocup.dynamic_object.player import Agent
from robocup.rules.field import FieldModel

from numpy import ndarray


# La classe Team permet de gérer chaque Agent d'une équipe en s'implifiant la gestion
# par la boucle de jeu.
class Team:
    def __init__(self, color_team: str, color_num_action_dict: Dict[str, int], color_agent_dict: Dict[str, Agent]):
        self.color_team: str = color_team
        self.color_num_action_dict: Dict[str, int] = color_num_action_dict
        self.color_agent_dict: Dict[str, Agent] = color_agent_dict
        self._points: int = 0
        # self.policy = RandomPolicy()

    # Distribue les valeurs comprises dans le tableau de tableau d'action et les distribut à chaque agents
    #
    #   Paramètres :
    #   ------------
    #   action: List[int]
    #        Le tableau de tableau d'action de taille 7 comprenant un booléen pour chaque type d'actions (avancer,
    #        reculer, aller à droite, aller à gauche, tourner à droite, tourner à gauche, tirer)
    #
    #   Sorties
    #   -------
    #   None
    def set_actions(self, *args) -> None:
        action_list = [*args]
        for color_agent, num_action in self.color_num_action_dict.items():
            agent = self.color_agent_dict[color_agent]
            if num_action < len(action_list):
                agent.set_action(action_list[num_action])
            else:
                # action = self.policy.predict()
                action = [0, 0, 0, 0, 0, 0, 0]
                agent.set_action(action)

    # Met à jour la position, l'angle de rotation et la vitesse de chaque agent de l'équipe
    #
    #   Paramètres :
    #   ------------
    #   field_model: FieldModel
    #       field_model contient les positions de chaque élément sur le terrain.
    #       On l'utilise donc pour récupérer la position, largeur, longueur, ... de chaque objet sur le terrain
    #
    #   Sorties
    #   -------
    #   None
    def update(self, field_model: FieldModel) -> None:
        for agent in self.color_agent_dict.values():
            agent.update(field_model=field_model)

    # Met à jour les informations des différents éléments de l'espace d'observation par état pour chaque
    # agent de l'équipe
    #   Paramètres :
    #   ------------
    #   ball: Ball
    #       Objet balle dans lequel on va récupérer l'état
    #   opponents_dict
    #       Dictionnaire contenant tous les agents ennemis dont on va récupérer l'état
    #   Sorties
    #   -------
    #   None
    def update_state(self, ball, opponents_dict) -> None:
        for color_agent, agent in self.color_agent_dict.items():
            allies_dict = self.color_agent_dict.copy()
            del allies_dict[color_agent]
            agent.update_state(ball, allies_dict, opponents_dict)

    # Retourne un Agent en fonction de sa couleur
    # agent de l'équipe
    #   Paramètres :
    #   ------------
    #   color_agent: string
    #       Couleur de l'agent qu'on veut récupérer
    #   opponents_dict
    #       Dictionnaire contenant tous les agents ennemis dont on va récupérer l'état
    #   Sorties
    #   agent: Agent
    #       Retourne l'agent de l'équipe de la couleur demandé
    def get_agent(self, color_agent) -> Agent:
        return self.color_agent_dict.get(color_agent)

    # Remets la position de chaque agent de l'équipe à sa position initial définit au début du jeu
    #
    #   Paramètres :
    #   ------------
    #   None
    #
    #   Sorties
    #   -------
    #   None
    def reset_position(self) -> None:
        for agent in self.color_agent_dict.values():
            agent.reset_position()

    # Remets la position de chaque agent de l'équipe à sa position d'après mi-temps
    #
    #   Paramètres :
    #   ------------
    #   None
    #
    #   Sorties
    #   -------
    #   None
    def reset_position_after_mid_game(self) -> None:
        for agent in self.color_agent_dict.values():
            agent.reset_position_after_mid_game()

    # Gère la collision et /oule tir de chaque agent sur la balle
    #   Paramètres :
    #   ------------
    #   ball: Ball
    #       Objet ball sur lequel on va appliquer la collision et/ou le tir
    #   Sorties
    #   -------
    #   bool
    #       Renvoie le dernier Agent qui a touché la balle
    def manage_interaction_with_ball(self, ball: Ball) -> Agent:
        last_touched: Agent = None
        for agent in self.color_agent_dict.values():
            if agent.manage_collision_with_ball(ball):
                last_touched = agent

        for agent in self.color_agent_dict.values():
            if agent.manage_shot_rotated(ball=ball):
                last_touched = agent
        return last_touched

    @property
    def points(self) -> int:
        return self._points

    @points.setter
    def points(self, points: int) -> None:
        self._points = points

    # Retourne la matrice d'observation par état vu par chaque agent de l'équipe
    #   Paramètres :
    #   ------------
    #   None
    #
    #   Sorties
    #   -------
    #   Dict[str,ndarray]
    #       la matrice d'observation par état de chaque agent de l'équipe
    def get_observation(self) -> Dict[str, ndarray]:

        color_state_dict = {}

        for color_agent, agent in self.color_agent_dict.items():
            color_state_dict[color_agent] = agent.get_observation()

        return color_state_dict
