from robocup.dynamic_object.player import *

import math

import numpy as np

np.set_printoptions(threshold=20, precision=3, suppress=True, linewidth=200)


class Ball:
    # used for the ball
    def __init__(self, x: float, y: float, r: float, color: str):
        self.x: float = x
        self.y: float = y
        self.prev_x: float = self.x
        self.prev_y: float = self.y
        self.vx: float = 0
        self.vy: float = 0
        self.r: float = r
        self.color: str = color

        self.init_x: float = x
        self.init_y: float = y

    # Attribut à la balle une vitesse quand elle est tirée par un agent
    #
    #   Paramètres :
    #   ------------
    #   agent : Agent
    #       Agent effectuant le tir sur la balle
    #   power : float
    #       Puissance de tir de l'agent sur la balle
    #
    #   Sorties
    #   -------
    #   None
    def ball_is_shot(self, agent: Agent, power: float) -> None:
        abx = self.x - agent.x
        aby = self.y - agent.y

        self.vx = abx * power
        self.vy = aby * power

    # Vérifie si la balle est entrée en collision avec un agent (distance entre la balle et l'agent inférieur à la
    # somme de leur rayon respectif)
    #
    #   Paramètres :
    #   ------------
    #   agent : Agent
    #       Agent sur lequel on vérifie s'il est entré en collision avec la balle
    #
    #   Sorties
    #   -------
    #   True -> Il y a une collision sinon False
    def is_colliding(self, agent: Agent) -> bool:
        r = self.r + agent.r
        return r * r > self.get_dist(agent)  # if distance is less than total radius, then colliding.

    # Permet de modifier la position de la balle lorsque l'agent "pousse" la balle sans tirer
    #
    #   Paramètres :
    #   ------------
    #   agent : Agent
    #       Agent avec lequel la balle est entrée en collision
    #
    #   Sorties
    #   -------
    #   None
    def collision_with_player(self, agent: Agent) -> None:
        abx = self.x - agent.x
        aby = self.y - agent.y
        abd = math.sqrt(abx * abx + aby * aby)
        if abd == 0:
            print("Attention, division par 0 détectée !!")
            return
        abx /= abd  # normalize
        aby /= abd
        nx = abx  # reuse calculation
        ny = aby
        abx *= NUDGE
        aby *= NUDGE
        while self.is_colliding(agent):
            self.x += abx
            self.y += aby
        ux = self.vx - agent.vx
        uy = self.vy - agent.vy
        un = ux * nx + uy * ny
        unx = nx * (un * 2.)  # added factor of 2
        uny = ny * (un * 2.)  # added factor of 2
        ux -= unx
        uy -= uny
        self.vx = (ux + agent.vx) * 0.1
        self.vy = (uy + agent.vy) * 0.1

    # Gère la collision et le rebond de la balle contre les poteaux des cages de but
    #
    #   Paramètres :
    #   ------------
    #   field_model: FieldModel
    #       field_model contient les positions de chaques éléments sur le
    #       terrain. On l'utilise donc pour récupérer la position, largeur, longueur, ...
    #
    #   Sorties
    #   -------
    #   None
    def collision_with_goal(self, field_model: FieldModel) -> None:

        goal_left_x = field_model.goal_data.get('goal_left_x')
        goal_y = field_model.goal_data.get('goal_y')
        goal_width = field_model.goal_data.get('goal_width')
        goal_height = field_model.goal_data.get('goal_height')

        goal_density = field_model.goal_data.get('goal_density')

        goal_right_x = field_model.goal_data.get('goal_right_x')

        circle_x = self.x
        circle_y = self.y
        circle_radius = self.r

        collision_dict_rect_1 = collision_rectangle_circle(goal_left_x, goal_y,
                                                           goal_width + field_model.field_line_density, -goal_density,
                                                           circle_x, circle_y, circle_radius)
        collision_dict_rect_2 = collision_rectangle_circle(goal_left_x, goal_y, goal_density, -goal_height, circle_x,
                                                           circle_y, circle_radius)
        collision_dict_rect3 = collision_rectangle_circle(goal_left_x, (goal_y - goal_height) + goal_density,
                                                          goal_width + field_model.field_line_density, -goal_density,
                                                          circle_x, circle_y, circle_radius)

        collision_dict_rect_4 = collision_rectangle_circle(goal_right_x - field_model.field_line_density, goal_y,
                                                           goal_width + field_model.field_line_density, -goal_density,
                                                           circle_x, circle_y, circle_radius)
        collision_dict_rect_5 = collision_rectangle_circle((goal_right_x + goal_width) - goal_density, goal_y,
                                                           goal_density, -goal_height, circle_x, circle_y,
                                                           circle_radius)
        collision_dict_rect_6 = collision_rectangle_circle(goal_right_x - field_model.field_line_density,
                                                           (goal_y - goal_height) + goal_density,
                                                           goal_width + field_model.field_line_density, -goal_density,
                                                           circle_x, circle_y, circle_radius)

        self.update_position_and_speed_after_collision_with_goal(goal_left_x,
                                                                 goal_left_x + goal_width + field_model.field_line_density,
                                                                 goal_y,
                                                                 goal_y - goal_density, collision_dict_rect_1)

        self.update_position_and_speed_after_collision_with_goal(goal_left_x, goal_left_x + goal_density, goal_y,
                                                                 goal_y - goal_height, collision_dict_rect_2)

        self.update_position_and_speed_after_collision_with_goal(goal_left_x,
                                                                 goal_left_x + goal_width + field_model.field_line_density,
                                                                 (goal_y - goal_height) + goal_density,
                                                                 goal_y - goal_height, collision_dict_rect3)

        self.update_position_and_speed_after_collision_with_goal(goal_right_x,
                                                                 goal_right_x + goal_width,
                                                                 goal_y,
                                                                 goal_y - goal_density, collision_dict_rect_4)

        self.update_position_and_speed_after_collision_with_goal((goal_right_x + goal_width) - goal_density,
                                                                 goal_right_x + goal_width,
                                                                 goal_y,
                                                                 goal_y - goal_height, collision_dict_rect_5)

        self.update_position_and_speed_after_collision_with_goal(goal_right_x,
                                                                 goal_right_x + goal_width,
                                                                 (goal_y - goal_height) + goal_density,
                                                                 goal_y - goal_height, collision_dict_rect_6)

    # Partie fonctionnelle de la fonction collision_with_goal()
    #
    #   Paramètres :
    #   ------------
    #   new_x_left: float
    #       Position en x du coin en bas à gauche
    #   new_x_right: float
    #       Position en x du coin en bas à droite
    #   new_y_up: float
    #       Position en y du haut du carré
    #   new_y_down: float
    #       Position en y du bas du carré
    #   collision_dict_rect: Dict[str, bool]
    #       Dictionnaire {clé=endroit de la collision, valeur=booléen collision ou non}
    #
    #   Sorties
    #   -------
    #   None
    def update_position_and_speed_after_collision_with_goal(self, new_x_left: float, new_x_right: float,
                                                            new_y_up: float,
                                                            new_y_down: float,
                                                            collision_dict_rect: Dict[str, bool]) -> None:

        if collision_dict_rect.get('left'):

            self.vx *= -FRICTION
            self.x = new_x_left - self.r

        elif collision_dict_rect.get('right'):

            self.vx *= -FRICTION
            self.x = new_x_right + self.r

        elif collision_dict_rect.get('up'):

            self.vy *= -FRICTION
            self.y = new_y_up + self.r

        elif collision_dict_rect.get('down'):

            self.vy *= -FRICTION
            self.y = new_y_down - self.r

    # Actualise la position et la vitesse de la balle après un pas de temps.
    # On vérifie également s'il y a une collision avec une cage de but ou la fenêtre de jeu
    #
    #   Paramètres :
    #   ------------
    #   field_model: FieldModel
    #       field_model contient les positions de chaque élément sur le
    #       terrain. On l'utilise donc pour récupérer la position, largeur, longueur, ...
    #
    #   Sorties
    #   -------
    #   None
    def update(self, field_model: FieldModel) -> None:
        self.prev_x = self.x
        self.prev_y = self.y
        self.x += self.vx * TIMESTEP
        self.y += self.vy * TIMESTEP

        self.collision_with_goal(field_model=field_model)

        if self.x - self.r <= -field_model.field_width / 2:
            self.vx *= - FRICTION
            self.x = -field_model.field_width / 2 + self.r

        if self.x + self.r >= field_model.field_width / 2:
            self.vx *= -FRICTION
            self.x = field_model.field_width / 2 - self.r

        if self.y + self.r >= field_model.field_height:
            self.vy *= -FRICTION
            self.y = field_model.field_height - self.r

        if self.y - self.r <= 0:
            self.vy *= -FRICTION
            self.y = self.r

        self.vx *= FRICTION
        self.vy *= FRICTION

    # Calcule la distance entre un agent et la balle
    #
    #   Paramètres :
    #   ------------
    #   agent : Agent
    #       Agent avec lequel on vérifie la distance
    #
    #   Sorties
    #   -------
    #   float : retourne la distance au carré entre le centre de la balle et le centre du joueur
    def get_dist(self, agent: Agent) -> float:  # returns distance squared from p
        dy = agent.y - self.y
        dx = agent.x - self.x
        return dx * dx + dy * dy

    # Remets la position de la balle à sa position initiale au tout début du jeu (Le centre du terrain)
    #
    #   Paramètres :
    #   ------------
    #   None
    #
    #   Sorties
    #   -------
    #   None
    def reset_position(self) -> None:

        self.x = self.init_x
        self.y = self.init_y
        self.vx = 0
        self.vy = 0
