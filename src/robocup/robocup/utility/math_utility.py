from typing import Dict

from robocup.view.geom import *

# Utiliser pour déterminer si un cercle est en collision avec un rectangle
# formule basée sur ce site http://www.jeffreythompson.org/collision-detection/circle-rect.php la formule est adaptée
# car l'origine du repère cartésien (0,0) est en haut à gauche sur le site (y décroît suivant l'ordonnée bas en haut)
# dans notre cas l'origine du repère est en bas à gauche (y s'accroît suivant l'ordonnée de bas en haut)
#     Paramètres
#     ----------
#     rect_x : float
#          coordonnées x du point en haut à gauche du rectangle
#     rect_y : float
#          coordonnées y du point en haut à gauche du rectangle
#     rect_width : float
#          largeur du rectangle
#     rect_height : float
#          hauteur du rectangle
#     circle_x : float
#          coordonnées x du cercle
#     circle_y : float
#          coordonnées y du cercle
#     circle_radius : float
#          rayon du cercle
#
#     Sorties
#     -------
#     Dict[str, bool]
#         Dictionnaire {clé=endroit de la collision, valeur=booléen collision ou non}


def collision_rectangle_circle(rect_x: float, rect_y: float,
                               rect_width: float, rect_height: float, circle_x: float, circle_y: float,
                               circle_radius: float) -> Dict[str, bool]:
    test_x = circle_x
    test_y = circle_y

    collision_dict = {'left': False, 'right': False, 'up': False, 'down': False}

    collision_side = ''

    if circle_x < rect_x:
        test_x = rect_x
        collision_side = 'left'
    elif circle_x > rect_x + rect_width:
        test_x = rect_x + rect_width
        collision_side = 'right'

    if circle_y > rect_y:
        test_y = rect_y
        collision_side = 'up'
    elif circle_y < rect_y + rect_height:
        test_y = rect_y + rect_height
        collision_side = 'down'

    dist_x = circle_x - test_x
    dist_y = circle_y - test_y

    distance = math.sqrt((math.pow(dist_x, 2)) + (math.pow(dist_y, 2)))

    if distance <= circle_radius:
        collision_dict[collision_side] = True
    return collision_dict


# formale basée sur un code javascript
# https://stackoverflow.com/questions/4465931/rotate-rectangle-around-a-point/13208761
# http://jsfiddle.net/dahousecat/4TtvU/
# Cette formule permet de transformer les coordonnées d'un point après une rotation autour de l'axe (origine)
# On peut s'en servir par exemple pour faire tourner un rectangle, l'origine étant le milieu du rectangle
# L'angle en paramètre est en degrés, il est converti en radians dans le code

#     Paramètres
#     ----------
#     point_x : float
#          coordonnées x du point
#     point_y : float
#          coordonnées y du point
#     origin_x : float
#          coordonnées x de l'origine
#     origin_y : float
#          coordonnées y de l'origine
#     angle : float
#          angle d'inclinaison par rapport à l'origine (en degrès)
#     Sorties
#     -------
#     Point
#         Coordonnées du point après conversion

def rotate_point(point_x: float, point_y: float, origin_x: float, origin_y: float, angle: float) -> Point:
    new_angle = angle * math.pi / 180.0

    new_point_x = math.cos(new_angle) * (point_x - origin_x) - math.sin(new_angle) * (point_y - origin_y) + origin_x
    new_point_y = math.sin(new_angle) * (point_x - origin_x) + math.cos(new_angle) * (point_y - origin_y) + origin_y

    return Point(new_point_x, new_point_y)


# Formule basée sur plusieurs recherches https://www.wyzant.com/resources/answers/601887/calculate-point-given-x-y
# -angle-and-distance On peut se servir de cette fonction pour déterminer les coordonnées d'un point suivant l'axe de
# rotation et la vitesse. Dans le code de AgentRect l'axe de rotation correspond à l'origine du rectangle

#     Paramètres
#     ----------
#     point_x : float
#          coordonnées x du point
#     point_y : float
#          coordonnées y du point
#     origin_angle : float
#          angle d'inclinaison par rapport l'origine (en degrès)
#     radius_x : float
#          distance en x par rapport à l'origine
#     radius_y : float
#          distance en y par rapport à l'origine
#     Sorties
#     -------
#     Point
#         Coordonnées du point après conversion

def convert_coordinates_with_angle_and_radius(point_x: float, point_y: float, origin_angle: float, radius_x: float,
                                              radius_y: float) -> Point:
    theta = math.radians(origin_angle)

    new_point_x = point_x + (radius_x * math.cos(theta))
    new_point_y = point_y + (radius_y * math.sin(theta))

    return Point(new_point_x, new_point_y)


# http://www.jeffreythompson.org/collision-detection/circle-circle.php

#     Détecte la collision entre deux cercles
#     Paramètres
#     ----------
#     circle1_x : float
#          coordonnées x du cercle 1
#     circle1_y : float
#          coordonnées y du cercle 1
#     circle1_radius : float
#          rayon du cercle 1
#     circle2_x : float
#           coordonnées x du cercle 2
#     circle2_y : float
#          coordonnées y du cercle 2
#     circle2_y : float
#          rayon du cercle 2
#     Sorties
#     -------
#     bool
#         retourne vrai si il y a une collision, faux dans le cas contraire

def collision_circle_circle(circle1_x: float, circle1_y: float, circle1_radius: float, circle2_x: float,
                            circle2_y: float, circle2_radius: float) -> bool:
    dist_x = circle1_x - circle2_x
    dist_y = circle1_y - circle2_y

    distance = math.sqrt(math.pow(dist_x, 2) + math.pow(dist_y, 2))

    if distance <= circle1_radius + circle2_radius:
        return True
    return False
