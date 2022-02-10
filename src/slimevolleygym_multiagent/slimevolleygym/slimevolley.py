"""
Update version of slimeVolleyGym developed by David Ha (2020)
Project : PDP 2020-2021 : Apprentissage par renforcement multi-agents : De Slimevolley à la Robocup
Author : Alexis HOFFMANN, Alexis LHERITIER, Nicolas MAJOREL, Pélagie ALVES, Elias DEBEYSSAC, Yves-Sébastian PAGES
Last update : 03 March 2021
Description : This version is an adaptation of SlimeVolleyGym
written by David Ha in 2020. This version contains only the "STATE"
game mode.This version is a gateway to implement the Robocup version.

Feature : SlimeVolleyGym_MultiAgent implements the team concept, JSON
config reader, CSV writer and multi-agent environment.

Source :
Port of Neural Slime Volleyball to Python Gym Environment
David Ha (2020)
Original version:
https://otoro.net/slimevolley
https://blog.otoro.net/2015/03/28/neural-slime-volleyball/
https://github.com/hardmaru/neuralslimevolley
No dependencies apart from Numpy and Gym
"""

import logging
import math
from typing import Tuple

import gym
from gym import spaces
from gym.utils import seeding
from gym.envs.registration import register
import numpy as np
import cv2  # installed with gym anyways
from collections import deque
from lib import jsonLib, csvLib

np.set_printoptions(threshold=20, precision=3, suppress=True, linewidth=200)

# initialisation of the i/o files
jsonIn = jsonLib.jsonInput('env.json')

# game settings:
REF_W = 24 * 2
REF_H = REF_W
REF_U = 1.5  # ground height
REF_WALL_WIDTH = 1.0  # wall width
REF_WALL_HEIGHT = 3.5
PLAYER_SPEED_X = 10 * 1.75
PLAYER_SPEED_Y = 10 * 1.35
MAX_BALL_SPEED = 15 * 1.5
TIMESTEP = 1 / 30.
NUDGE = 0.1
FRICTION = 1.0  # 1 means no FRICTION, less means FRICTION
INIT_DELAY_FRAMES = 30
GRAVITY = -9.8 * 2 * 1.5

MAXLIVES = 5  # game ends when one agent loses this many games

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 500

FACTOR = WINDOW_WIDTH / REF_W

NB_AGENTS = jsonIn.get_value_from_Json("env", "nb_agent_by_team") * 2
NB_BALLS = 1


# if set to true, renders using cv2 directly on numpy array
# (otherwise uses pyglet / opengl -> much smoother for human player)

def setNightColors():
    ### night time color:
    global BALL_COLOR, TEAM_LEFT_COLOR, TEAM_RIGHT_COLOR
    global BACKGROUND_COLOR, FENCE_COLOR, COIN_COLOR, GROUND_COLOR
    BALL_COLOR = (217, 79, 0)
    TEAM_LEFT_COLOR = (0, 0, 255)
    TEAM_RIGHT_COLOR = (255, 0, 0)
    BACKGROUND_COLOR = (11, 16, 19)
    FENCE_COLOR = (102, 56, 35)
    COIN_COLOR = FENCE_COLOR
    GROUND_COLOR = (116, 114, 117)
    global COLOR
    COLOR = {'red': (255, 0, 0), 'blue': (0, 0, 255), 'purple': (128, 0, 128), 'green': (0, 128, 0),
             'yellow': (255, 255, 0), 'white': (255, 255, 255)}


setNightColors()

# by default, don't load rendering (since we want to use it in headless cloud machines)
rendering = None


############### GLOBAL FUNCTION #############################
def checkRendering():
    global rendering
    if rendering is None:
        from gym.envs.classic_control import rendering as rendering


# conversion from space to pixels (allows us to render to diff resolutions)
def toX(x):
    return (x + REF_W / 2) * FACTOR


def toP(x):
    return (x) * FACTOR


def toY(y):
    return y * FACTOR


def check_if_duplicate(list_e):
    for elem in list_e:
        if list_e.count(elem) > 1:
            return True
    return False


def invert_dict(dict_e):
    return dict(map(reversed, dict_e.items()))


class DelayScreen:
    """ initially the ball is held still for INIT_DELAY_FRAMES(30) frames """

    def __init__(self, life=INIT_DELAY_FRAMES):
        self.life = 0
        self.reset(life)

    def reset(self, life=INIT_DELAY_FRAMES):
        self.life = life

    def status(self):
        if self.life == 0:
            return True
        self.life -= 1
        return False


def make_half_circle(radius=10, res=20, filled=True):
    """ helper function for pyglet renderer"""
    points = []
    for i in range(res + 1):
        ang = math.pi - math.pi * i / res
        points.append((math.cos(ang) * radius, math.sin(ang) * radius))
    if filled:
        return rendering.FilledPolygon(points)
    else:
        return rendering.PolyLine(points, True)


def _add_attrs(geom, color):
    """ help scale the colors from 0-255 to 0.0-1.0 (pyglet renderer) """
    r = color[0]
    g = color[1]
    b = color[2]
    geom.set_color(r / 255., g / 255., b / 255.)


# Fonction de création d'un canvas rectangulaire basique pour la couleur d'arrière-plan
def create_canvas(canvas, c):
    rect(canvas, 0, 0, WINDOW_WIDTH, -WINDOW_HEIGHT, c)
    return canvas


# Fonction de création d'un rectagle
# return : Canvas de l'objet rectangle
# x -> position en x du rectangle
# y -> position en y du rectangle
# width -> largeur du rectangle
# height -> hauteur du rectangle
# color -> couleur du rectangle
def rect(canvas, x, y, width, height, color):
    """ Processing style function to make it easy to port p5.js program to python """
    box = rendering.make_polygon([(0, 0), (0, -height), (width, -height), (width, 0)])
    trans = rendering.Transform()
    trans.set_translation(x, y)
    _add_attrs(box, color)
    box.add_attr(trans)
    canvas.add_onetime(box)
    return canvas


# Fonction de création d'un demi-cercle
# return : Canvas de l'objet demi-cercle
# x -> position en x du demi-cercle
# y -> position en y du demi-cercle
# r -> rayon du demi-cercle
# color -> couleur du demi-cercle
def half_circle(canvas, x, y, r, color):
    geom = make_half_circle(r)
    trans = rendering.Transform()
    trans.set_translation(x, y)
    _add_attrs(geom, color)
    geom.add_attr(trans)
    canvas.add_onetime(geom)
    return canvas


# Fonction de création d'un cercle
# return : Canvas de l'objet cercle
# x -> position en x du cercle
# y -> position en y du cercle
# r -> rayon du cercle
# color -> couleur du cercle
def circle(canvas, x, y, r, color):
    geom = rendering.make_circle(r, res=40)
    trans = rendering.Transform()
    trans.set_translation(x, y)
    _add_attrs(geom, color)
    geom.add_attr(trans)
    canvas.add_onetime(geom)
    return canvas


############### CLASS #############################

# Class utilisé pour gérer la balle et pour le bout rond au-dessus du mur
# Cette class permet d'afficher, de déplacer la balle, limiter la vitesse
# Elle permet également de gérer la collision entre les différents éléments
# sur le terrain et de rebondir après une collision
# Paramètre :
# x -> position en x
# y -> position en y
# vx -> vitesse en x
# vy ->  vitesse en y
# r -> rayon de l'objet
# c -> couleur de l'objet
class Particle:
    """ used for the ball, and also for the round stub above the fence """

    def __init__(self, x, y, vx, vy, r, c):
        self.x = x
        self.y = y
        self.prev_x = self.x
        self.prev_y = self.y
        self.vx = vx
        self.vy = vy
        self.r = r
        self.c = c

    # Permet d'afficher l'objet balle
    def display(self, canvas):
        return circle(canvas, toX(self.x), toY(self.y), toP(self.r), color=self.c)

    # Modifie la position de la balle pour simuler son déplacement
    def move(self):
        self.prev_x = self.x
        self.prev_y = self.y
        self.x += self.vx * TIMESTEP
        self.y += self.vy * TIMESTEP

    # Permet de simuler
    def applyAcceleration(self, ax, ay):
        self.vx += ax * TIMESTEP
        self.vy += ay * TIMESTEP

    # Vérifie s'il y a une collision entre un élément et la balle
    def checkEdges(self):
        if self.x <= (self.r - REF_W / 2):
            self.vx *= -FRICTION
            self.x = self.r - REF_W / 2 + NUDGE * TIMESTEP

        if self.x >= (REF_W / 2 - self.r):
            self.vx *= -FRICTION
            self.x = REF_W / 2 - self.r - NUDGE * TIMESTEP

        if self.y <= (self.r + REF_U):
            self.vy *= -FRICTION
            self.y = self.r + REF_U + NUDGE * TIMESTEP
            if self.x <= 0:
                return -1
            else:
                return 1
        if self.y >= (REF_H - self.r):
            self.vy *= -FRICTION
            self.y = REF_H - self.r - NUDGE * TIMESTEP
        # fence:
        if ((self.x <= (REF_WALL_WIDTH / 2 + self.r)) and (self.prev_x > (REF_WALL_WIDTH / 2 + self.r)) and (
                self.y <= REF_WALL_HEIGHT)):
            self.vx *= -FRICTION
            self.x = REF_WALL_WIDTH / 2 + self.r + NUDGE * TIMESTEP

        if ((self.x >= (-REF_WALL_WIDTH / 2 - self.r)) and (self.prev_x < (-REF_WALL_WIDTH / 2 - self.r)) and (
                self.y <= REF_WALL_HEIGHT)):
            self.vx *= -FRICTION
            self.x = -REF_WALL_WIDTH / 2 - self.r - NUDGE * TIMESTEP
        return 0

    # Return la distance au carré entre la balle et un objet p
    def getDist2(self, p):
        dy = p.y - self.y
        dx = p.x - self.x
        return dx * dx + dy * dy

    # Return Vrai s'il y a une collision entre la balle et un objet
    def isColliding(self, p):
        r = self.r + p.r
        return r * r > self.getDist2(p)  # Si la distance est inférieur au carré du rayon, alors il y a une collision

    # Simule un rebond de la balle après une collision avec un agent ou un mur
    def bounce(self, p):
        abx = self.x - p.x
        aby = self.y - p.y
        abd = math.sqrt(abx * abx + aby * aby)
        abx /= abd  # normalize
        aby /= abd
        nx = abx  # reuse calculation
        ny = aby
        abx *= NUDGE
        aby *= NUDGE
        while self.isColliding(p):
            self.x += abx
            self.y += aby
        ux = self.vx - p.vx
        uy = self.vy - p.vy
        un = ux * nx + uy * ny
        unx = nx * (un * 2.)  # added factor of 2
        uny = ny * (un * 2.)  # added factor of 2
        ux -= unx
        uy -= uny
        self.vx = ux + p.vx
        self.vy = uy + p.vy

    # Limite la vitesse de la balle
    def limitSpeed(self, minSpeed, maxSpeed):
        mag2 = self.vx * self.vx + self.vy * self.vy;
        if mag2 > (maxSpeed * maxSpeed):
            mag = math.sqrt(mag2)
            self.vx /= mag
            self.vy /= mag
            self.vx *= maxSpeed
            self.vy *= maxSpeed

        if mag2 < (minSpeed * minSpeed):
            mag = math.sqrt(mag2)
            self.vx /= mag
            self.vy /= mag
            self.vx *= minSpeed
            self.vy *= minSpeed


## Classe utilisé pour définir et afficher le mur au centre du terrain ainsi que le sol du terrain
# Paramètre :
# x -> position en x
# y -> position en y
# w -> largeur de l'objet
# h -> hauteur de l'objet
# c -> couleur de l'objet
class Wall:
    def __init__(self, x, y, w, h, c):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.c = c

    # affiche le mur ou le sol à l'écran
    def display(self, canvas):
        return rect(canvas, toX(self.x - self.w / 2), toY(self.y + self.h / 2), toP(self.w), toP(self.h), color=self.c)


class RelativeState:
    """
    keeps track of the obs.
    Note: the observation is from the perspective of the agent.
    an agent playing either side of the fence must see obs the same way
    """

    def __init__(self):
        # agent
        self._x = 0
        self._y = 0
        self._vx = 0
        self._vy = 0
        # ball

        self._bx = 0
        self._by = 0
        self._bvx = 0
        self._bvy = 0

        # allies Dict['color': [x, y, vx, vy]]
        self._allies_color_state_dict = {}

        # opponents Dict['color': [x, y, vx, vy]]
        self._opponents_color_state_dict = {}

    def set_agent_state(self, state: Tuple[float, float, float, float]):
        self._x = state[0]
        self._y = state[1]
        self._vx = state[2]
        self._vy = state[3]

    def set_ball_state(self, state: Tuple[float, float, float, float]):
        self._bx = state[0]
        self._by = state[1]
        self._bvx = state[2]
        self._bvy = state[3]

    def set_allies_color_state_dict(self, state: Tuple[str, Tuple[float, float, float, float]]):
        self._allies_color_state_dict[state[0]] = list(state[1])

    def set_opponents_color_state_dict(self, state: Tuple[str, Tuple[float, float, float, float]]):
        self._opponents_color_state_dict[state[0]] = list(state[1])

    # La méthode retourne des observations relatives par rapport à l'agent, la balle, ses alliés et
    #  l'équipe adverse (position en x, position en y, vitesse en x, vitesse en y), ces données sont utilisées
    #   pour l'espace d'observation par états (observation_space)
    def getObservation(self):
        unpack_allies_color_state_dict = [*self._allies_color_state_dict.values()]
        unpack_opponents_color_state_dict = [*self._opponents_color_state_dict.values()]

        # print(unpack_allies_color_state_dict)
        # print(unpack_opponents_color_state_dict)
        result = [self._x, self._y, self._vx,
                  self._vy, self._bx, self._by,
                  self._bvx, self._bvy] + \
                 [j for i in unpack_allies_color_state_dict for j in i] + \
                 [j for i in unpack_opponents_color_state_dict for j in i]
        scaleFactor = 10.0  # scale inputs to be in the order of magnitude of 10 for neural network.
        result = np.array(result) / scaleFactor
        return result


## Classe utilisé pour définir et gérer un agent. On peut définir une action pour l'agent, l'afficher,
# actualiser sa position sur le terrain et actualiser l'espace d'observation qu'il peut voir.
# Paramètre :
# x -> position en x
# y -> position en y
# dir -> position sur le terrain (-1 -> gauche, +1 -> droite)
# color_agent -> couleur de l'agent
class Agent:
    """ keeps track of the agent in the game """

    def __init__(self, dir, x, y, color_agent):

        self.dir = dir
        self.x = x
        self.y = y
        self.r = 1.5
        self.color_agent = color_agent
        self.vx = 0
        self.vy = 0
        self.desired_vx = 0
        self.desired_vy = 0
        self.state = RelativeState()

    #  action: tableau [forward, backward, jump] d'entiers de 0 à 1, 0 l'action n'est pas demandée,
    # 1 l'action est demandée, met à jour la vitesse désirée selon les actions demandées
    def set_action(self, action):
        forward = False
        backward = False
        jump = False
        if action[0] > 0:
            forward = True
        if action[1] > 0:
            backward = True
        if action[2] > 0:
            jump = True
        self.desired_vx = 0
        self.desired_vy = 0
        if forward and (not backward):
            self.desired_vx = -PLAYER_SPEED_X
        if backward and (not forward):
            self.desired_vx = PLAYER_SPEED_X
        if jump:
            self.desired_vy = PLAYER_SPEED_Y

    def move(self):
        self.x += self.vx * TIMESTEP
        self.y += self.vy * TIMESTEP

    def step(self):
        self.x += self.vx * TIMESTEP
        self.y += self.vy * TIMESTEP

    # Gestion de la vitesse et de la position de l'agent par rapport aux interactions avec les bordures du jeu
    # et au filet en fonction de la vitesse désirée (action demandée -> contrôle sur l'environnement)
    def update(self):
        self.vy += GRAVITY * TIMESTEP

        if self.y <= REF_U + NUDGE * TIMESTEP:
            self.vy = self.desired_vy

        self.vx = self.desired_vx * self.dir

        self.move()

        if self.y <= REF_U:
            self.y = REF_U
            self.vy = 0

        # stay in their own half:
        if self.x * self.dir <= (REF_WALL_WIDTH / 2 + self.r):
            self.vx = 0
            self.x = self.dir * (REF_WALL_WIDTH / 2 + self.r)

        if self.x * self.dir >= (REF_W / 2 - self.r):
            self.vx = 0
            self.x = self.dir * (REF_W / 2 - self.r)

    # Met à jour les informations des différents éléments de l'espace d'observation par états de l'agent appelant
    def update_state(self, ball, allies_dict, opponents_dict):

        self.update_self_state()
        self.update_ball_state(ball)
        self.update_allies_state(allies_dict)
        self.update_opponents_state(opponents_dict)

    # informations relatives de l'agent appelant
    def update_self_state(self):

        agent_x = self.x * self.dir
        agent_y = self.y
        agent_vx = self.vx * self.dir
        agent_vy = self.vy

        self.state.set_agent_state((agent_x, agent_y, agent_vx, agent_vy))

    # informations relatives de la balle par rapport à l'agent appelant
    def update_ball_state(self, ball):

        bx = ball.x * self.dir
        by = ball.y
        bvx = ball.vx * self.dir
        bvy = ball.vy

        self.state.set_ball_state((bx, by, bvx, bvy))

    # informations relatives des alliés par rapport à l'agent appelant
    def update_allies_state(self, allies_dict):

        for ally_color, ally in allies_dict.items():
            ally_x = ally.x * self.dir
            ally_y = ally.y
            ally_vx = ally.vx * self.dir
            ally_vy = ally.vy

            self.state.set_allies_color_state_dict((ally_color, (ally_x, ally_y, ally_vx, ally_vy)))

    # informations relatives de l'équipe adverse par rapport à l'agent appelant
    def update_opponents_state(self, opponents_dict):

        for opponent_color, opponent in opponents_dict.items():
            opponent_x = opponent.x * (-self.dir)
            opponent_y = opponent.y
            opponent_vx = opponent.vx * (-self.dir)
            opponent_vy = opponent.vy

            self.state.set_opponents_color_state_dict(
                (opponent_color, (opponent_x, opponent_y, opponent_vx, opponent_vy)))

    # retourne les observations par états relatives à l'agent appelant
    def getObservation(self):
        return self.state.getObservation()

    #  Modifie et retourne le canvas en ajoutant le canvas du slime appelant, canvas: (Viewer Object), life: points de vie de l'équipe, color_team:
    #  couleur de l'équipe
    def display(self, canvas, life, color_team):
        x = self.x
        y = self.y
        r = self.r

        # draw the agent
        canvas = half_circle(canvas, toX(x), toY(y), toP(r + 0.2), color=COLOR[self.color_agent])
        canvas = half_circle(canvas, toX(x), toY(y), toP(r), color=COLOR[color_team])

        # draw coins (lives) left
        for i in range(1, life):
            canvas = circle(canvas, toX(self.dir * (REF_W / 2 + 0.5 - i * 2.)), WINDOW_HEIGHT - toY(1.5), toP(0.5),
                            color=COIN_COLOR)
        return canvas


class Game:
    """
    the main slime volley game.
    can be used in various settings, such as ai vs ai, ai vs human, human vs human
    """

    def __init__(self, team_left_dict, team_right_dict, np_random=np.random):
        self.ball = None
        self.ground = None
        self.fence = None
        self.fenceStub = None

        self.team_left: Team = None
        self.team_right: Team = None

        self.delayScreen = None

        self.team_left_dict = team_left_dict
        self.team_right_dict = team_right_dict

        self.np_random = np_random

        self.reset()

    # Réinitialise l'environnement de jeu, création du sol, du filet, initialisation de la vitesse initiale de la balle,
    # création de la balle, création des équipes, mis à jour des informations relatives des équipes
    def reset(self):
        #### DO NOT MODIFY
        self.ground = Wall(0, 0.75, REF_W, REF_U, c=GROUND_COLOR)
        self.fence = Wall(0, 0.75 + REF_WALL_HEIGHT / 2, REF_WALL_WIDTH, (REF_WALL_HEIGHT - 1.5), c=FENCE_COLOR)
        self.fenceStub = Particle(0, REF_WALL_HEIGHT, 0, 0, REF_WALL_WIDTH / 2, c=FENCE_COLOR);
        ball_vx = self.np_random.uniform(low=-20, high=20)
        ball_vy = self.np_random.uniform(low=10, high=25)
        self.ball = Particle(0, REF_W / 4, ball_vx, ball_vy, 0.5, c=BALL_COLOR)

        self.team_left = Team('red', -1, 2, self.team_left_dict)
        self.team_right = Team('blue', 1, 2, self.team_right_dict)

        self.team_right.updateState(self.ball, self.team_left.agent_dict)
        self.team_left.updateState(self.ball, self.team_right.agent_dict)

        ### DO NOT MODIFY
        self.delayScreen = DelayScreen()

    # Repositionne la balle au-dessus du filet à chaque nouvelle manche avec une vitesse aléatoire bornée par un certain intervalle
    def newMatch(self):
        ball_vx = self.np_random.uniform(low=-20, high=20)
        ball_vy = self.np_random.uniform(low=10, high=25)
        self.ball = Particle(0, REF_W / 4, ball_vx, ball_vy, 0.5, c=BALL_COLOR);
        self.delayScreen.reset()

    # Mis à jour des équipes, contrôle de l'accélération de la balle, contrôle de la collision entre
    # les agents d'une même équipe, rebondissement de la balle sur les agents en cas de collision,
    # vérifie si la balle est tombée sur le sol d'une du camp d'une certaine équipe,
    # retourne le résultat de l'action sur l'environnement selon la perspective de l'équipe de droite :
    # 0 : la balle est encore en jeu.
    # 1 : la balle est tombée dans le camp de l'équipe gauche.
    # -1 : la balle est tombée dans le camp de l'équipe droite.
    # met à jour les informations relatives des agents
    def step(self):
        self.team_left.update()
        self.team_right.update()
        if self.delayScreen.status():
            self.ball.applyAcceleration(0, GRAVITY)
            self.ball.limitSpeed(0, MAX_BALL_SPEED)
            self.ball.move()
        self.team_right.isCollisionBetweenTeamMates()
        self.team_left.isCollisionBetweenTeamMates()
        for agent in self.team_left.agent_dict.values():
            if self.ball.isColliding(agent):
                self.ball.bounce(agent)
        for agent in self.team_right.agent_dict.values():
            if self.ball.isColliding(agent):
                self.ball.bounce(agent)
        if self.ball.isColliding(self.fenceStub):
            self.ball.bounce(self.fenceStub)
        result = -self.ball.checkEdges()
        if result != 0:
            self.newMatch()  # not reset, but after a point is scored
            if result < 0:  # baseline agent won
                self.team_right.life -= 1
            else:
                self.team_left.life -= 1
            return result
        # update internal states (the last thing to do)
        self.team_left.updateState(self.ball, self.team_right.agent_dict)
        self.team_right.updateState(self.ball, self.team_left.agent_dict)
        return result

    # Modifie le canvas (Viewer Object) en ajoutant les canvas des élements de l'environnement:
    # - filet
    # - équipes
    # - balle
    # - sol
    def display(self, canvas):
        # background color
        canvas = create_canvas(canvas, c=BACKGROUND_COLOR)
        canvas = self.fence.display(canvas)
        canvas = self.fenceStub.display(canvas)

        canvas = self.team_left.display_team(canvas)
        canvas = self.team_right.display_team(canvas)

        canvas = self.ball.display(canvas)
        canvas = self.ground.display(canvas)
        return canvas


# Choisit une action aléatoire [forward, backward, jump]
class RandomPolicy:
    def __init__(self):
        self.action_space = gym.spaces.MultiBinary(3)
        pass

    def predict(self):
        return self.action_space.sample()


class SlimeVolleyMultiAgentEnv(gym.Env):
    # La partie se finit quadn une équipe perd 5 matches (ou après 3000 timesteps(pas temporel)).

    # Classe principale implémentant l'interface Env, gestion du cycle de vie
    # de l'environnement, exécution d'actions dans celui-ci, récupération des résultats
    # d'une action sur l'environnement
    metadata = {
        'render.modes': ['human', 'rgb_array', 'state'],
        'video.frames_per_second': 50

    }

    def __init__(self, team_left_dict={'purple': 0, 'green': 1}, team_right_dict={'yellow': 2, 'white': 3}):
        # les paramètres team_left_dict et team_right_dict permettent d'indiquer
        # à l'utilisateur quelles couleurs d'agents sont associées (en plus de la couleur de l'équipe) aux actions récupérées dans step
        # pour pouvoir distinguer quels modèles sont utilisés par les agents
        # par défaut l'agent que l'on entraîne est celui qui récupère la première action dans step (compatibilité avec les
        # algorithmes dans stable_baselines) -> agent_being_trained

        # step(action, action1, action2, action3, ...)
        self.team_left_dict = team_left_dict
        self.team_right_dict = team_right_dict

        both_team_list = [*team_left_dict.values(), *team_right_dict.values()]

        # print(both_team_list)

        filtered = filter(lambda num_action: num_action < 0 or num_action >= 4, both_team_list)

        list_filtered = list(filtered)

        # print(len(list_filtered))

        assert len(list_filtered) == 0
        assert check_if_duplicate(both_team_list) == False
        self.t = 0
        self.t_limit = 3000

        # On construit l'espace d'actions, vecteur de booléens
        # [forward, backward, jump] -> (0: l'action n'est pas demandée, 1: l'action est demandée)
        # Cet attribut est utilisé par différents algorithmes d'apprentissage par renforcement
        # par exemple: PPO
        self.action_space = spaces.MultiBinary(3)

        # On construit l'espace d'observations, vecteurs de flottants, intervalle de valeurs acceptées
        # Contient les positions et les vitesses des agents et de la balle, selon la perspective d'un agent donné
        # [agent_x, agent_y, agent_vx, agent_vy, ball_x, ball_y, ball_vx, ball_vy, ally1_x, ally1_y, ally1_vx, ally1_vy, ... , ally2_x, ...
        # , opponent1_x, opponent1_y, opponent1_vx, opponent1_vy, ... , opponent2_x, ...]
        high = np.array([np.finfo(np.float32).max] * ((NB_AGENTS * 4) + (NB_BALLS * 4)))
        self.observation_space = spaces.Box(-high, high)

        # Création du jeu, porte de communication principale entre l'environnement et le fonctionnement interne.
        self.game = Game(self.team_left_dict, self.team_right_dict)

        self.agent_being_trained = None
        self.ale = None
        self.update_agent_being_trained()

        # self.ale = # for compatibility for some models that need the self.ale.lives() function
        self.viewer = None

    # Met à jour l'agent que l'on entraîne, nécessaire quand on réinitialise le jeu (Game)

    def update_agent_being_trained(self):

        my_inverted_team_left_dict = invert_dict(self.team_left_dict)
        my_inverted_team_right_dict = invert_dict(self.team_right_dict)

        if my_inverted_team_left_dict.__contains__(0):
            color_agent = my_inverted_team_left_dict[0]
            self.agent_being_trained = self.game.team_left.get_agent(color_agent)
        elif my_inverted_team_right_dict.__contains__(0):
            color_agent = my_inverted_team_right_dict[0]
            self.agent_being_trained = self.game.team_right.get_agent(color_agent)

        self.ale = self.agent_being_trained
        # print(self.agent_being_trained)

    # Génération de la graine aléatoire, utilisée pour trouver une vitesse aléatoire pour la balle à chaque nouvelle manche
    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        self.game = Game(self.team_left_dict, self.team_right_dict, np_random=self.np_random)
        ## Version modifier pour qu'on puisse entraîner que le tout premier agent Allié (id = 0)
        # self.ale = self.game.agent_right  # for compatibility for some models that need the self.ale.lives() function
        self.update_agent_being_trained()
        return [seed]

    # retourne les observations par états relatives à l'agent entraîné
    def getObs(self):
        obs = self.agent_being_trained.getObservation()
        return obs

    # méthode principale qui permet d'interagir avec l'environnement
    # action: action que l'on exécute sur l'agent que l'on entraîne, [forward, backward, jump] -> 0, 1
    # *args: plusieurs actions pour plusieurs autres agents
    # args[0] = [1, 1, 0], args[1] = [1, 0, 0] etc ...
    # le numéro de l'action récupérée pour chacun des agens est définie par les dictionnaires team_left_dict, team_right_dict

    # exécute une action et renvoie un tuple (obs, reward, done, info)
    # obs (selon la perspective de l'agent entraîné), reward (selon la perspective de l'équipe de droite), done: booléen: le jeu est terminé (une équipe a gagné ou le
    # temps de jeu est dépassé), info: informations auxiliaires (pour débuguer)

    ### TODO
    # - reward en fonction de l'équipe de l'agent entraîné
    # - ajouter les observations des autres agents dans le dictionnaire info
    def step(self, action, *args):
        done = False
        self.t += 1
        assert len(args) <= NB_AGENTS - 1

        if len(action) != NB_AGENTS:
            self.game.team_left.set_actions(action)
            self.game.team_right.set_actions(action)
        else:  # Nous sommes dans le cas ou le nombre de joueur est de 4 pour un apprentissage
            # On entraine toujours le premier agent de gauche
            action_left = action[0], action[1]
            self.game.team_left.set_multiple_actions(action_left)
            action_right = action[2], action[3]
            self.game.team_right.set_multiple_actions(action_right)

        reward = self.game.step()

        obs = self.getObs()

        if self.t >= self.t_limit:
            done = True
        if self.game.team_left.life <= 0 or self.game.team_right.life <= 0:
            done = True

        # {'team_left_dict': {'purple': 0, 'green': 1}, 'team_right_dict': {'yellow': 2, 'white': 3}}
        ## On récupère l'observation générale depuis l'un des joueurs de la team
        all_agent_right = self.game.team_right.get_all_agent()
        all_agent_left = self.game.team_left.get_all_agent()

        info = {
            'ale.lives': self.game.team_right.lives(),
            'ale.otherLives': self.game.team_left.lives(),
            'otherObs': all_agent_left[0].getObservation(),
            'state': all_agent_right[0].getObservation(),
            'otherEnnemyState': all_agent_left[1].getObservation(),
            'otherAllyState': all_agent_right[1].getObservation(),
        }

        return obs, reward, done, info

    def init_game_state(self):
        self.t = 0
        self.game.reset()
        self.update_agent_being_trained()

    # réintialise l'environnement et retourne les observations par états de l'agent entraîné
    def reset(self):
        self.init_game_state()
        return self.getObs()

    # rendu de l'environnement en utilisant l'objet Viewer
    def render(self, mode='human', close=False):
        if self.viewer is None:
            checkRendering()
            self.viewer = rendering.Viewer(WINDOW_WIDTH, WINDOW_HEIGHT)

        self.game.display(self.viewer)
        return self.viewer.render(return_rgb_array=mode == 'rgb_array')

    def close(self):
        if self.viewer:
            self.viewer.close()


# La classe Team permet de gérer chaque Agent d'une équipe en s'implifiant la gestion
# par la boucle de jeu.
class Team:
    def __init__(self, color_team, dir, n, color_num_action_agent_dict):
        self.agent_dict = {}
        self.color_team = color_team
        self.life = MAXLIVES
        self.dir = dir
        self.n = n
        self.general_state = None
        self.policy = RandomPolicy()
        assert n == len(color_num_action_agent_dict)
        self.color_num_action_agent_dict = color_num_action_agent_dict
        self.create_team()

    # Créer automatiquement une équipe en fonction du
    # nombre de joueur choisi à la construction de la classe Team
    def create_team(self):
        i = 0
        if self.dir == -1:
            for color_agent in self.color_num_action_agent_dict:
                self.agent_dict[color_agent] = Agent(self.dir, -(i + 1) * (REF_W / 6), 1.5, color_agent)
                i = i + 1
        elif self.dir == 1:
            for color_agent in self.color_num_action_agent_dict:
                self.agent_dict[color_agent] = Agent(self.dir, (i + 1) * (REF_W / 6), 1.5, color_agent)
                i = i + 1
        # print(self.agent_dict)

    # Affecte une action à un agent
    def set_actions(self, *args):
        action_list = [*args]
        for color_agent, num_action in self.color_num_action_agent_dict.items():
            agent = self.agent_dict[color_agent]
            if num_action < len(action_list):
                agent.set_action(action_list[num_action])
            else:
                action = self.policy.predict()
                agent.set_action(action)

    def set_multiple_actions(self, args):
        cpt = 0
        for agent in self.get_all_agent():
            agent.set_action(args[cpt])
            cpt += 1

    # Met à jour la position de chaque Agent
    def update(self):
        # print(self.agent_dict)
        for agent in self.agent_dict.values():
            agent.update()

    # Met à jour la table d'état de chaque Agent
    def updateState(self, ball, opponents_dict):
        for color_agent, agent in self.agent_dict.items():
            allies_dict = self.agent_dict.copy()
            del allies_dict[color_agent]
            agent.update_state(ball, allies_dict, opponents_dict)
            self.general_state = agent.getObservation()

    ## Retourne la distance entre 2 Agents
    def getDistBetweenTeamMates(self, a1, a2):
        dy = a2.y - a1.y
        dx = a2.x - a1.x
        return math.sqrt(dx * dx + dy * dy)

    ## Retourne la distance par rapport à un cercle dessiné depuis le point situé en a1 - r
    def getDistLeftAgent(self, a1, a2):
        dy = a2.y - a1.y - a1.r
        dx = a2.x - a1.x - a1.r
        return math.sqrt(dx * dx + dy * dy)

    ## Retourne la distance par rapport à un cercle dessiné depuis le point situé en a1 + r
    def getDistRightAgent(self, a1, a2):
        dy = a2.y - a1.y + a1.r
        dx = a2.x - a1.x + a1.r
        return math.sqrt(dx * dx + dy * dy)

    # Dans cette partie nous gérons la collision quand un agent allié "glisse" sur un des côté d'un autre
    # agent. Pour cela, nous faisons glissé l'agent sur un cercle dont le centre est situé sur chaque
    # extrémité droite et gauche du slime
    def collisionLeftCircle(self, agent_list, agent1, agent2):
        if self.getDistLeftAgent(agent_list[agent1], agent_list[agent2]) < agent_list[agent1].r:
            agent_list[agent1].vy = 0
            agent_list[agent1].vx = 0
            agent_list[agent1].y = agent_list[agent1].y + 2
            agent_list[agent1].x = agent_list[agent1].x - 2

    def collisionRightCircle(self, agent_list, agent1, agent2):
        if self.getDistRightAgent(agent_list[agent1], agent_list[agent2]) < agent_list[agent1].r:
            agent_list[agent2].vy = 0
            agent_list[agent2].vx = 0
            agent_list[agent2].y = agent_list[agent2].y + 2
            agent_list[agent2].x = agent_list[agent2].x + 2

    # Permet de gérer la collision entre deux Agents allié
    ## TODO : Corriger la valuation de l'écart entre les deux slimes(ne pas prendre une valeur fixe)
    ## TODO : Prendre en compte le fait que le pas à chaque update peut faire entrer le slime dans son allié
    def isCollisionBetweenTeamMates(self):
        agent_list = [*self.agent_dict.values()]
        isColliding = False
        for agent1 in range(len(agent_list)):
            for agent2 in range(agent1 + 1, len(agent_list)):
                dist = self.getDistBetweenTeamMates(agent_list[agent1], agent_list[agent2])
                ## Fonction temporaire pour gérer la collision entre 2 agents
                if dist <= 2 * agent_list[agent1].r:
                    reste = 2 * agent_list[agent1].r - dist
                    agent_list[agent2].vx = 0
                    agent_list[agent2].vy = 0
                    agent_list[agent2].x = agent_list[agent2].x + reste
                    agent_list[agent2].y = agent_list[agent2].y + reste
                    isColliding = True
        return isColliding
        # Ici, on vérifie fait la collision quand les slimes sont à la même hauteur. La distance parfaite
        # les séparants est de 2 fois le rayon d'un slime.
        # if agent_list[agent1].y == agent_list[agent2].y:
        #     if dist < agent_list[agent1].r + agent_list[agent2].r:
        #         agent_list[agent1].vx = 0
        #         agent_list[agent2].vx = 0
        #         if agent_list[agent1].x < agent_list[agent2].x:
        #             agent_list[agent1].x = agent_list[agent1].x - 1
        #             agent_list[agent2].x = agent_list[agent2].x + 1
        #         else:
        #             agent_list[agent1].x = agent_list[agent1].x + 1
        #             agent_list[agent2].x = agent_list[agent2].x - 1
        #
        # # On vérifie si L'agent (agent1 ou agent2) est "pile" au-dessus de l'agent. On utilise une marge de plus ou
        # # moins le rayon de l'agent le plus bas car quand l'agent au-dessus est entre + ou - le rayon de celui
        # # d'en-dessous. Alors, sa partie basse est toujours en contact avec le point le plus haut de l'agent
        # # d'en bas. La distance les séparants est de 1 fois le rayon de l'agent le plus bas
        # elif agent_list[agent1].y < agent_list[agent2].y:
        #     if agent_list[agent1].x - agent_list[agent1].r < agent_list[agent2].x < agent_list[agent1].x + agent_list[agent1].r:
        #         agent_list[agent2].vy = 0
        #         agent_list[agent2].y = agent_list[agent2].y + 2
        #     elif agent_list[agent1].x < agent_list[agent2].x:
        #         self.collisionRightCircle(agent_list, agent1, agent2)
        #     elif agent_list[agent1].x > agent_list[agent2].x:
        #         self.collisionLeftCircle(agent_list, agent1, agent2)
        #
        # elif agent_list[agent1].y > agent_list[agent2].y:
        #     if agent_list[agent2].x - agent_list[agent2].r < agent_list[agent1].x < agent_list[agent2].x + agent_list[agent2].r:
        #         agent_list[agent1].vy = 0
        #         agent_list[agent1].y = agent_list[agent2].y + 2
        #     elif agent_list[agent2].x > agent_list[agent1].x:
        #         self.collisionRightCircle(agent_list, agent1, agent2)
        #     elif agent_list[agent2].x < agent_list[agent1].x:
        #         self.collisionLeftCircle(agent_list, agent1, agent2)

    ## Retourne le nombre de vie de l'équipe
    def lives(self):
        return self.life

    ## Permet d'afficher chaque Agent de l'équipe
    ## en appelant la fonction d'affichage d'un Agent
    def display_team(self, canvas):
        for agent in self.agent_dict.values():
            canvas = agent.display(canvas, self.life, self.color_team)
        return canvas

    # Retourne un Agent en fonction de sa couleur
    def get_agent(self, color_agent):
        return self.agent_dict.get(color_agent)

    def get_all_agent(self):
        return [*self.agent_dict.values()]


#####################
# helper functions: #
#####################

def multiagent_rollout(env, policy_right_1, policy_right_2, policy_left_train, policy_left_2, render_mode=False):
    """
    play one agent vs the other in modified gym-style loop.
    important: returns the score from perspective of policy_right.
    """
    obs_right = env.reset()
    obs_left = obs_right  # same observation at the very beginning for the other agent

    done = False
    total_reward = 0
    t = 0

    while not done:
        action_left_train = policy_left_train.predict(obs_left)
        action_left_2 = policy_left_2.predict(obs_left)
        action_right_1 = policy_right_1.predict(obs_right)
        action_right_2 = policy_right_2.predict(obs_right)

        all_actions = [action_left_train, action_left_2, action_right_1, action_right_2]

        # uses a 2nd (optional) parameter for step to put in the other action
        # and returns the other observation in the 4th optional "info" param in gym's step()
        obs_right, reward, done, info = env.step(all_actions)
        obs_left = info['otherObs']

        total_reward += reward
        t += 1

        if render_mode:
            env.render()
    return total_reward, t


####################
# Reg envs for gym #
####################

register(
    id=jsonIn.get_value_from_Json("id"),
    entry_point='slimevolleygym.slimevolley:SlimeVolleyMultiAgentEnv',
    kwargs=jsonIn.get_value_from_Json("arguments")
    # {'team_left_dict': {'purple': 0, 'green': 1}, 'team_right_dict': {'yellow': 2, 'white': 3}}

)
