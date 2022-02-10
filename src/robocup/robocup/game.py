from robocup.dynamic_object.ball import Ball, Agent
from robocup.dynamic_object.team import Team
from robocup.rules.referee import Referee
from robocup.spec.settings import *

from robocup.rules.field import *

from numpy import ndarray

import copy

np.set_printoptions(threshold=20, precision=3, suppress=True, linewidth=200)


class DelayScreen:
    """ initially the ball is held still for INIT_DELAY_FRAMES(30) frames """

    def __init__(self, life=INIT_DELAY_FRAMES):
        self.life: int = 0
        self.reset(life)

    def reset(self, life=INIT_DELAY_FRAMES) -> None:
        self.point = life

    def status(self) -> bool:
        if self.life == 0:
            return True
        self.life -= 1
        return False


# Classe principale de la robocup
# Elle contient toutes les méthodes nécessaires pour initialiser le jeu et lancer une partie
class Game:

    def __init__(self, field_model: FieldModel, team_left: Team, team_right: Team,
                 ball: Ball, referee: Referee, delay_screen: DelayScreen, color_agent_being_trained: str):

        self.field_model: FieldModel = field_model

        self.team_left: Team = team_left
        self.team_right: Team = team_right
        self.ball: Ball = ball

        self.referee: Referee = referee

        self.delay_screen: DelayScreen = delay_screen

        self._initial_game = self
        self.mid_game = 1

        self.color_agent_being_trained = color_agent_being_trained

        self.team_left.update_state(ball=self.ball, opponents_dict=self.team_right.color_agent_dict)
        self.team_right.update_state(ball=self.ball, opponents_dict=self.team_left.color_agent_dict)

    # Permet de replacer automatiquement à la position initiale de jeu la balle et les agents
    #
    #   Paramètres :
    #   ------------
    #   None
    #
    #   Sorties
    #   -------
    #   None
    #
    def new_match(self) -> None:
        self.ball.reset_position()
        self.team_left.reset_position()
        self.team_right.reset_position()
        self.referee.last_touched = None

    # Place les agents dans la nouvelle configuration post mi-temps
    #
    #   Paramètres :
    #   ------------
    #   None
    #
    #   Sorties
    #   -------
    #   None
    #
    def mid_game_event(self):
        self.ball.reset_position()
        self.team_left.reset_position_after_mid_game()
        self.team_right.reset_position_after_mid_game()
        self.mid_game = -1
        self.referee.last_touched = None

    # Boucle de jeu classique d'une partie
    #
    #   Paramètres :
    #   ------------
    #   None
    #
    #   Sorties
    #   -------
    #   int
    #       Retourne le résultat d'un tour de boucle. 0 pas de but, 1 ou -1 en fonction de la perspective de l'agent
    def step(self) -> int:
        # L'arbitre vérifie qu'il y a une collision entre les agents
        self.referee.is_collision_between_agent_left()
        self.referee.is_collision_between_agent_right()
        self.referee.is_collision_between_team()

        # On met à jour la position des agents
        self.team_left.update(self.field_model)
        self.team_right.update(self.field_model)

        # On vérifie qu'il y a une collision entre la nouvelle position des agents et la balle
        last_touched_left: Agent = self.team_left.manage_interaction_with_ball(ball=self.ball)
        last_touched_right: Agent = self.team_right.manage_interaction_with_ball(ball=self.ball)

        last_touched: Agent = None
        if last_touched_left is not None and last_touched_right is None:
            last_touched = last_touched_left
        elif last_touched_right is not None:
            last_touched = last_touched_right

        # On met à jour la position de la balle
        self.ball.update(self.field_model)

        # On met à jour les différents éléments stockés par l'arbitre
        self.referee.update_referee(self.team_left, self.team_right, self.ball, last_touched)

        # on vérifie qu'aucun agent est en dehors du terrain
        self.referee.is_agent_outside_field()

        # On vérifie qu'il y a un but
        if self.referee.is_ball_outside_goal_line() is not None and not self.referee.is_goal():
            print(
                "Il y a corner/6 mètres l'arbitre !!! C'est " + self.referee.last_touched.color_agent + "qui l'a mit "
                                                                                                        "dehors")
            self.new_match()
        if self.referee.is_ball_outside_sideline() is not None:
            print("Il y a touche l'arbitre !!! C'est " + self.referee.last_touched.color_agent + " qui l'a mit dehors")
            self.new_match()

        result = self.referee.is_goal() * self.mid_game

        if result != 0:
            self.new_match()  # Remet chaque joueur + la balle à la position de base
            if result > 0:  # l'agent de droite marque un but
                points = self.team_right.points
                print("point équipe bleu")
                self.team_right.points = points + 1
            else:  # l'agent de gauche marque un but
                points = self.team_left.points
                print("point équipe rouge")
                self.team_left.points = points + 1

        self.team_left.update_state(ball=self.ball, opponents_dict=self.team_right.color_agent_dict)
        self.team_right.update_state(ball=self.ball, opponents_dict=self.team_left.color_agent_dict)

        result = self._convert_result_from_agent_being_trained_perspective(result=result)
        return result

    def reset(self):
        # pattern prototype
        return copy.deepcopy(self._initial_game)

    # la récompense de referee est selon la perspective de l'équipe de droite
    # inversion du résultat, si l'agent est dans l'équipe de gauche
    #
    #   Paramètres :
    #   ------------
    #   int
    #       Résultat récupéré du match
    #
    #   Sorties
    #   -------
    #   int
    #       Retourne le résultat d'un tour de boucle. 0 pas de but, 1 ou -1 en fonction de la perspective de l'agent
    def _convert_result_from_agent_being_trained_perspective(self, result: int):
        if self.color_agent_being_trained in self.team_left.color_agent_dict.keys():
            result = -result
        return result

    # Récupère l'espace d'observation vue par l'agent entrainé
    #
    #   Paramètres :
    #   ------------
    #   None
    #
    #   Sorties
    #   -------
    #   ndarray
    #       Retourne l'espace d'observation vue par l'agent entrainé
    def get_agent_being_trained_observation(self) -> ndarray:
        if self.color_agent_being_trained in self.team_left.color_agent_dict.keys():
            agent = self.team_left.color_agent_dict[self.color_agent_being_trained]
            return agent.get_observation()
        elif self.color_agent_being_trained in self.team_right.color_agent_dict.keys():
            agent = self.team_right.color_agent_dict[self.color_agent_being_trained]
            return agent.get_observation()

    # Récupère l'espace d'observation de tous les agents sauf celui en train d'être entrainé
    #
    #   Paramètres :
    #   ------------
    #   None
    #
    #   Sorties
    #   -------
    #   Dict[str, ndarray]
    #       Retourne un dictionnaire d'espace d'observation vue par chaque agent
    def get_other_observation(self) -> Dict[str, ndarray]:
        color_state_dict = {}

        team_left_color_state_dict = self.team_left.get_observation()
        team_right_color_state_dict = self.team_right.get_observation()

        color_state_dict.update(team_left_color_state_dict)
        color_state_dict.update(team_right_color_state_dict)

        del color_state_dict[self.color_agent_being_trained]

        return color_state_dict
