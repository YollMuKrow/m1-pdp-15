from typing import List

from numpy import ndarray

from robocup.dynamic_object.state import RelativeState
from robocup.rules.field import *
from robocup.utility.math_utility import *

np.set_printoptions(threshold=20, precision=3, suppress=True, linewidth=200)


# Adaptation dans l'environnement robocup d'un agent slimevolley
class Agent:

    def __init__(self, direction: int, x: float, y: float, radius: float,
                 color_agent: str, origin_angle: float, relative_state: RelativeState):
        self.dir: int = direction  # -1 means left, 1 means right player for symmetry.
        self.x: float = x
        self.y: float = y
        self.r: float = radius
        self.color_agent: str = color_agent

        self.vx: float = 0
        self.vy: float = 0
        self.desired_vx: float = 0
        self.desired_vy: float = 0

        self.state: RelativeState = relative_state

        self.init_x: float = x  # position initiale en x de l'agent au début d'une partie
        self.init_y: float = y  # position initiale en y de l'agent au début d'une partie
        self.is_shooting: bool = False
        self.desired_angle: float = 0
        self.origin_angle: float = origin_angle
        self.init_origin_angle: float = self.origin_angle

        self.point_eye_left: Point = \
            convert_coordinates_with_angle_and_radius(point_x=self.x, point_y=self.y,
                                                      origin_angle=self.origin_angle + 29,
                                                      radius_x=self.r * 3 / 4,
                                                      radius_y=self.r * 3 / 4)
        self.point_eye_right: Point = \
            convert_coordinates_with_angle_and_radius(point_x=self.x, point_y=self.y,
                                                      origin_angle=self.origin_angle - 29,
                                                      radius_x=self.r * 3 / 4,
                                                      radius_y=self.r * 3 / 4)
        self.point_init_eye_left: Point = self.point_eye_left
        self.point_init_eye_right: Point = self.point_eye_right

        self.is_left: bool = False
        self.is_right: bool = False
        self.point_circle_hitbox: Point = \
            convert_coordinates_with_angle_and_radius(point_x=self.x, point_y=self.y,
                                                      origin_angle=self.origin_angle,
                                                      radius_x=self.r, radius_y=self.r)

        self.circle_hitbox_radius: float = self.r / 1.5

        self.init_point_circle_hitbox: Point = self.point_circle_hitbox

    # Remets la position de l'agent à sa position initial définit au début du jeu
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

        self.origin_angle = self.init_origin_angle

        self.point_eye_left = self.point_init_eye_left
        self.point_eye_right = self.point_init_eye_right

        self.point_circle_hitbox = self.init_point_circle_hitbox

    # Remets la position de l'agent à sa position après la mi-temps
    #
    #   Paramètres :
    #   ------------
    #   None
    #
    #   Sorties
    #   -------
    #   None
    def reset_position_after_mid_game(self) -> None:
        self.reset_position()

        self.dir = self.dir * -1
        self.x = self.init_x * -1
        self.y = self.init_y

        self.origin_angle = self.init_origin_angle

        self.point_eye_left.x = self.point_init_eye_left.x * -1
        self.point_eye_right.x = self.point_init_eye_right.x * -1

        self.point_circle_hitbox.x = self.init_point_circle_hitbox.x * -1

    # Distribue les valeurs comprises dans le tableau d'action et les traduits en action
    #
    #   Paramètres :
    #   ------------
    #   action: List[int]
    #        Le tableau d'action de taille 7 comprenant un booléen pour chaque type d'actions (avancer, reculer,
    #        aller à droite, aller à gauche, tourner à droite, tourner à gauche, tirer)
    #
    #   Sorties
    #   -------
    #   None
    def set_action(self, action: List[int]) -> None:

        # move

        left = False
        right = False
        forward = False
        backward = False

        if action[0] > 0:
            left = True
        if action[1] > 0:
            right = True
        if action[2] > 0:
            forward = True
        if action[3] > 0:
            backward = True

        self.desired_vx = 0
        self.desired_vy = 0

        self.is_left = False
        self.is_right = False

        # on vérifie qu'il n'y a pas d'information contradictoire
        # exemple : avancer et reculer en même temps
        if left and (not right) and (not forward) and (not backward):
            self.desired_vx = PLAYER_SPEED_LEFT
            self.desired_vy = PLAYER_SPEED_LEFT
            self.is_left = True
        if right and (not left) and (not forward) and (not backward):
            self.desired_vx = -PLAYER_SPEED_RIGHT
            self.desired_vy = -PLAYER_SPEED_RIGHT
            self.is_right = True
        if forward and (not backward) and (not left) and (not right):
            self.desired_vx = PLAYER_SPEED_FORWARD
            self.desired_vy = PLAYER_SPEED_FORWARD
        if backward and (not forward) and (not left) and (not right):
            self.desired_vx = -PLAYER_SPEED_BACKWARD
            self.desired_vy = -PLAYER_SPEED_BACKWARD

        # shoot

        shoot = False

        if action[4] > 0:
            shoot = True

        self.is_shooting = False

        if shoot:
            self.is_shooting = True

        # rotate

        rotate_left = False
        rotate_right = False
        self.desired_angle = 0

        if action[5] > 0:
            rotate_left = True
        if action[6] > 0:
            rotate_right = True

        if rotate_left and not rotate_right:
            self.desired_angle = 1
            self.origin_angle = (self.origin_angle + self.desired_angle) % 360

        if rotate_right and not rotate_left:
            self.desired_angle = -1
            self.origin_angle = (self.origin_angle + self.desired_angle) % 360

    # Utiliser pour faire mouvoir l'agent sur le terrain avec tous les éléments le
    # composant (les yeux et la zone de tir )
    #
    #   Paramètres :
    #   ------------
    #   None
    #
    #   Sorties
    #   -------
    #   None
    def move(self) -> None:
        origin_angle = self.origin_angle

        if self.is_left or self.is_right:
            origin_angle = 90 + self.origin_angle

        point = convert_coordinates_with_angle_and_radius(point_x=self.x,
                                                          point_y=self.y,
                                                          origin_angle=origin_angle,
                                                          radius_x=self.vx * TIMESTEP,
                                                          radius_y=self.vy * TIMESTEP)

        self.x = point.x
        self.y = point.y

        self.point_eye_left = convert_coordinates_with_angle_and_radius(point_x=self.point_eye_left.x,
                                                                        point_y=self.point_eye_left.y,
                                                                        origin_angle=origin_angle,
                                                                        radius_x=self.vx * TIMESTEP,
                                                                        radius_y=self.vy * TIMESTEP)

        self.point_eye_right = convert_coordinates_with_angle_and_radius(point_x=self.point_eye_right.x,
                                                                         point_y=self.point_eye_right.y,
                                                                         origin_angle=origin_angle,
                                                                         radius_x=self.vx * TIMESTEP,
                                                                         radius_y=self.vy * TIMESTEP)

        self.point_circle_hitbox = convert_coordinates_with_angle_and_radius(point_x=self.point_circle_hitbox.x,
                                                                             point_y=self.point_circle_hitbox.y,
                                                                             origin_angle=origin_angle,
                                                                             radius_x=self.vx * TIMESTEP,
                                                                             radius_y=self.vy * TIMESTEP)

    # Utiliser pour faire tourner autour du point central de l'agent les différents éléments le composant
    # (yeux + zone de tir)
    #
    #   Paramètres :
    #   ------------
    #   None
    #
    #   Sorties
    #   -------
    #   None
    def rotate(self) -> None:

        self.point_eye_left = rotate_point(self.point_eye_left.x, self.point_eye_left.y, self.x,
                                           self.y, self.desired_angle)

        self.point_eye_right = rotate_point(self.point_eye_right.x, self.point_eye_right.y, self.x,
                                            self.y, self.desired_angle)

        self.point_circle_hitbox = rotate_point(self.point_circle_hitbox.x, self.point_circle_hitbox.y, self.x,
                                                self.y, self.desired_angle)

    # Calcule la prochaine position de l'agent en fonction de son futur angle
    #
    #   Paramètres :
    #   ------------
    #   None
    #
    #   Sorties
    #   -------
    #   Point
    #       La nouvelle position en x et y de l'agent
    def next_position(self) -> Point:

        next_vx = self.desired_vx * self.dir
        next_vy = self.desired_vy * self.dir

        origin_angle = self.origin_angle

        if self.is_left or self.is_right:
            origin_angle = 90 + self.origin_angle

        next_position = convert_coordinates_with_angle_and_radius(point_x=self.x,
                                                                  point_y=self.y,
                                                                  origin_angle=origin_angle,
                                                                  radius_x=next_vx * TIMESTEP,
                                                                  radius_y=next_vy * TIMESTEP)

        return next_position

    # Vérifie si l'agent ne se trouve pas en dehors du terrain
    #
    #   Paramètres :
    #   ------------
    #   x: float
    #       position en x du centre du joueur
    #   y: float
    #       position en y du centre du joueur
    #   field_model: FieldModel
    #       field_model contient les positions de chaque élément sur le terrain.
    #       On l'utilise donc pour récupérer la position, largeur, longueur, ... de chaque objet sur le terrain
    #
    #   Sorties
    #   -------
    #   bool
    #       True -> L'agent est en dehors du terrain sinon False
    def is_outside_field(self, x: float, y: float, field_model: FieldModel) -> bool:

        if x - self.r <= -field_model.field_width / 2:
            return True

        if x + self.r >= field_model.field_width / 2:
            return True

        if y + self.r >= field_model.field_height:
            return True

        if y - self.r <= 0:
            return True

        return False

    # Utilisé dans le cas d'une collision avec un autre joueur pour ne pas rentrer en collision physiquement avec lui
    #
    #   Paramètres :
    #   ------------
    #   None
    #
    #   Sorties
    #   -------
    #   None
    def cancel_movement(self):
        self.desired_vx = 0
        self.desired_vy = 0

    # Met à jour la position, son angle de rotation et la vitesse de l'agent
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
        next_position = self.next_position()

        if self.is_outside_field(x=next_position.x, y=next_position.y, field_model=field_model):
            self.cancel_movement()

        self.vx = self.desired_vx * self.dir
        self.vy = self.desired_vy * self.dir
        self.move()
        self.rotate()

    # Met à jour les informations des différents éléments de l'espace d'observation par état de l'agent appelant
    #   Paramètres :
    #   ------------
    #   ball: Ball
    #       Objet balle dans lequel on va récupérer l'état
    #   allies_dict
    #       Dictionnaire contenant tous les agents alliés dont on va récupérer l'état
    #   opponents_dict
    #       Dictionnaire contenant tous les agents ennemis dont on va récupérer l'état
    #   Sorties
    #   -------
    #   None
    def update_state(self, ball, allies_dict, opponents_dict):

        self.state.reset_state_observation_matrix()
        self.state.update_self_state(agent=self)
        self.state.update_ball_state(agent=self, ball=ball)
        self.state.update_allies_state(agent=self, allies_dict=allies_dict)
        self.state.update_opponents_state(agent=self, opponents_dict=opponents_dict)

    # Retourne la matrice d'observation par état vu par l'agent
    #   Paramètres :
    #   ------------
    #   None
    #
    #   Sorties
    #   -------
    #   ndarray
    #       la matrice d'observation par état de l'agent
    def get_observation(self) -> ndarray:
        return self.state.get_observation()

    # Gère le tir d'une balle lorsque l'agent n'est pas en rotation
    #   Paramètres :
    #   ------------
    #   ball: Ball
    #       Objet ball sur lequel on va appliquer le tir
    #   Sorties
    #   -------
    #   None
    # def manage_shot_not_rotated(self, ball) -> None:
    #
    #     if self.is_shooting:
    #         if ball.get_dist(self) <= (self.r + self.r / 1.5 * ball.r) * (
    #                 self.r + self.r / 1.5 * ball.r):
    #             ball.ball_is_shot(self, SHOT_POWER)

    # Gère le tir d'un agent sur une balle
    #   Paramètres :
    #   ------------
    #   ball: Ball
    #       Objet ball sur lequel on va appliquer le tir
    #   Sorties
    #   -------
    #   bool
    #       Renvoie True si on a tiré dans la balle, False sinon
    def manage_shot_rotated(self, ball) -> bool:
        if self.is_shooting:
            if collision_circle_circle(self.point_circle_hitbox.x, self.point_circle_hitbox.y,
                                       self.circle_hitbox_radius,
                                       ball.x, ball.y, ball.r):
                ball.ball_is_shot(self, SHOT_POWER)
                return True
            else:
                return False

    # Gère la collision d'un agent sur une balle
    #   Paramètres :
    #   ------------
    #   ball: Ball
    #       Objet ball sur lequel on va appliquer la collision
    #   Sorties
    #   -------
    #   bool
    #       Renvoie True si on est entré en collision avec la balle, False sinon
    def manage_collision_with_ball(self, ball) -> bool:
        if ball.is_colliding(self):
            ball.collision_with_player(self)
            return True
