from robocup.dynamic_object.ball import Ball
from robocup.dynamic_object.player import Agent
from robocup.dynamic_object.team import Team
from robocup.rules.field import FieldModel
from robocup.utility.math_utility import collision_circle_circle as collision, convert_coordinates_with_angle_and_radius


# Classe représentant l'arbitre d'une partie.
# L'arbitre contrôle s'il y a une collision entre Agent, vérifie s'il y a un but
# Il pourra plus tard gérer des fautes
class Referee:
    def __init__(self, team_left: Team, team_right: Team, field_model: FieldModel, ball: Ball):
        self.team_left: Team = team_left
        self.team_right: Team = team_right
        self.ball: Ball = ball
        self.last_touched: Agent = None
        self.field_model: FieldModel = field_model
        self.penalty_collision_enable = False
        self.collision_enable = False

    # Contrôle la collision entre 2 agents (agent1 et agent2) passé en paramètre
    #
    #   Paramètres
    #   ----------
    #       agent1_x: float
    #           position en x de l'agent 1
    #       agent1_y:float
    #           position en y de l'agent 1
    #       agent1_r:float
    #           rayon de l'agent 1
    #       agent2: Agent
    #           Objet agent contenant le second agent
    #   Sorties
    #   -------
    #   bool
    #       True s'il y a une collision, False sinon
    @staticmethod
    def is_collision_between_agent(agent1_x: float, agent1_y: float, agent1_r: float, agent2: Agent) -> bool:
        if collision(agent1_x, agent1_y, agent1_r, agent2.x, agent2.y, agent2.r):
            return True
        else:
            return False

    # L'arbitre vérifie la collision entre chaque membre de l'équipe gauche (on ne vérifie que quand le paramètre
    # collision_enable est activé)
    # On annule le mouvement d'un joueur s'il va rentrer en collision avec un joueur
    #
    #   Paramètres
    #   ----------
    #   None
    #
    #   Sorties
    #   -------
    #   bool
    #       True s'il y a eu une collision et que le paramètre pénalité collision est activé, False sinon
    def is_collision_between_agent_left(self):
        is_collision = False
        if self.collision_enable:
            for agent_left_1 in self.team_left.color_agent_dict.values():
                for agent_left_2 in self.team_left.color_agent_dict.values():
                    futur_point = agent_left_1.next_position()
                    if self.is_collision_between_agent(futur_point.x, futur_point.y, agent_left_1.r, agent_left_2) and \
                            agent_left_1 != agent_left_2:
                        agent_left_1.cancel_movement()
                        print("Collision agent Left")
                        is_collision = True
        if self.penalty_collision_enable:
            return is_collision

    # L'arbitre vérifie la collision entre chaque membre de l'équipe droite (on ne vérifie que quand le paramètre
    # collision_enable est activé)
    # On annule le mouvement d'un joueur s'il va rentrer en collision avec un joueur
    #
    #   Paramètres
    #   ----------
    #   None
    #
    #   Sorties
    #   -------
    #   bool
    #       True s'il y a eu une collision et que le paramètre pénalité collision est activé, False sinon
    def is_collision_between_agent_right(self):
        is_collision = False
        if self.collision_enable:
            for agent_right_1 in self.team_right.color_agent_dict.values():
                for agent_right_2 in self.team_right.color_agent_dict.values():
                    futur_point = agent_right_1.next_position()
                    if self.is_collision_between_agent(futur_point.x, futur_point.y, agent_right_1.r, agent_right_2) \
                            and agent_right_1 != agent_right_2:
                        print("Collision agent Right")
                        agent_right_1.cancel_movement()
                        is_collision = True
        if self.penalty_collision_enable:
            return is_collision

    # L'arbitre vérifie la collision entre chaque joueur des deux équipes
    # On annule le mouvement d'un joueur s'il va rentrer en collision avec un joueur
    #   Paramètres
    #   ----------
    #   None
    #
    #   Sorties
    #   -------
    #   bool
    #       True s'il y a eu une collision et que le paramètre pénalité collision est activé, False sinon
    def is_collision_between_team(self):
        # On vérifie la collision entre chaque membre des deux équipes
        is_collision = False
        if self.collision_enable:
            for agent_left in self.team_left.color_agent_dict.values():
                for agent_right in self.team_right.color_agent_dict.values():
                    futur_point_left = agent_left.next_position()
                    futur_point_right = agent_right.next_position()
                    if self.is_collision_between_agent(futur_point_left.x, futur_point_left.y, agent_left.r,
                                                       agent_right):
                        print("Collision between Team (left)")
                        agent_left.cancel_movement()
                        is_collision = True
                    if self.is_collision_between_agent(futur_point_right.x, futur_point_right.y, agent_right.r,
                                                       agent_left):
                        print("Collision between Team (right)")
                        agent_right.cancel_movement()
                        is_collision = True
        if self.penalty_collision_enable:
            return is_collision

    # Test si l'agent est hors du terrain côté ligne de touche
    #   Paramètres
    #   ----------
    #   agent: Agent
    #       agent sur lequel on va vérifier qu'il est bien dans le terrain
    #
    #   Sorties
    #   -------
    #   bool
    #       True si l'agent est hors du terrain, False sinon
    def is_agent_outside_sideline(self, agent: Agent) -> bool:
        sideline_data = self.field_model.side_line_data
        sideline_width = sideline_data.get("side_line_width")

        sideline_x = sideline_data.get("side_line_x")
        sideline_upper_y = sideline_data.get("side_line_y")
        sideline_bottom_y = sideline_upper_y - sideline_data.get("side_line_height")
        if sideline_x < agent.x < sideline_x + sideline_width and \
                (agent.y < sideline_bottom_y or agent.y > sideline_upper_y):
            return True
        return False

    # Test si l'agent est hors du terrain côté ligne de but
    #   Paramètres
    #   ----------
    #   agent: Agent
    #       agent sur lequel on va vérifier qu'il est bien dans le terrain
    #
    #   Sorties
    #   -------
    #   bool
    #       True si l'agent est hors du terrain, False sinon
    def is_agent_outside_goal_line(self, agent: Agent) -> bool:
        sideline_data = self.field_model.side_line_data
        sideline_width = sideline_data.get("side_line_width")

        sideline_x = sideline_data.get("side_line_x")
        sideline_upper_y = sideline_data.get("side_line_y")
        sideline_bottom_y = sideline_upper_y - sideline_data.get("side_line_height")
        if (sideline_x > agent.x or agent.x > sideline_x + sideline_width) and (
                sideline_bottom_y <= agent.y <= agent.y <= sideline_upper_y):
            return True
        return False

    # Test si l'agent est hors du terrain
    #   Paramètres
    #   ----------
    #   agent: Agent
    #       agent sur lequel on va vérifier qu'il est bien dans le terrain
    #
    #   Sorties
    #   -------
    #   bool
    #       True si l'agent est hors du terrain, False sinon
    def is_agent_outside_field(self):
        all_agent = {**self.team_right.color_agent_dict, **self.team_left.color_agent_dict}
        for agent in all_agent.values():
            if self.is_agent_outside_sideline(agent):
                print("Agent outside side line")
            if self.is_agent_outside_goal_line(agent):
                print("Agent outside goal line")

    # Test si la balle est hors du terrain (ligne de touche) et retourne le dernier agent à avoir touché la balle
    #   Paramètres
    #   ----------
    #   None
    #
    #   Sorties
    #   -------
    #   agent: Agent
    #       Retourne le dernier agent à avoir touché la balle None sinon
    # Retourne l'agent qui a mis la balle derrière la ligne de touche sinon None
    def is_ball_outside_sideline(self) -> bool:
        sideline_data = self.field_model.side_line_data
        sideline_width = sideline_data.get("side_line_width")

        sideline_x = sideline_data.get("side_line_x")
        sideline_upper_y = sideline_data.get("side_line_y")
        sideline_bottom_y = sideline_upper_y - sideline_data.get("side_line_height")
        if sideline_x < self.ball.x < sideline_x + sideline_width and \
                (self.ball.y < sideline_bottom_y or self.ball.y > sideline_upper_y):
            return self.last_touched
        return None

    # Test si la balle est hors du terrain (ligne de goal) et renvoi le dernier agent à avoir touché la balle
    #   Paramètres
    #   ----------
    #   None
    #
    #   Sorties
    #   -------
    #   agent: Agent
    #       Retourne le dernier agent à avoir touché la balle None sinon
    # Retourne l'agent qui a mis la balle derrière la ligne de touche sinon None
    def is_ball_outside_goal_line(self) -> bool:
        sideline_data = self.field_model.side_line_data
        sideline_width = sideline_data.get("side_line_width")

        sideline_x = sideline_data.get("side_line_x")
        sideline_upper_y = sideline_data.get("side_line_y")
        sideline_bottom_y = sideline_upper_y - sideline_data.get("side_line_height")
        if (sideline_x > self.ball.x or self.ball.x > sideline_x + sideline_width) and (
                sideline_bottom_y <= self.ball.y <= self.ball.y <= sideline_upper_y):
            return self.last_touched
        return None

    # Test si la balle est dans les cages d'une des équipes
    #   Paramètres
    #   ----------
    #   None
    #
    #   Sorties
    #   -------
    #   agent: Agent
    #       Retourne le dernier agent à avoir touché la balle None sinon
    # Retourne -1 si but dans les cages de gauche et 1 si but dans les cages de droite. 0 sinon
    def is_goal(self) -> int:
        goal_data = self.field_model.goal_data
        goal_left_x = goal_data.get("goal_left_x") + goal_data.get("goal_width")
        goal_right_x = goal_data.get("goal_right_x")

        goal_y = goal_data.get("goal_y")
        goal_height = goal_data.get("goal_height")

        if (self.ball.x <= goal_left_x) and (goal_y > self.ball.y > goal_y - goal_height):
            return 1
        if (self.ball.x >= goal_right_x) and (goal_y > self.ball.y > goal_y - goal_height):
            return -1
        return 0

    # Met à jour les valeurs de chaque joueur et de la balle utilisée par l'arbitre
    #   Paramètres
    #   ----------
    #   team_left: Team
    #       Objet Team contenant l'équipe de gauche
    #   team_right: Team
    #       Objet Team contenant l'équipe de droite
    #   ball: Ball
    #       Objet Ball contenant la balle
    #   last_touched: Agent
    #       Dernier agent à avoir touché la balle
    #
    #   Sorties
    #   -------
    #   None
    def update_referee(self, team_left: Team, team_right: Team, ball: Ball, last_touched: Agent) -> None:
        self.team_left = team_left
        self.team_right = team_right
        self.ball = ball
        if last_touched is not None:
            self.last_touched = last_touched
