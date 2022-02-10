import numpy as np

np.set_printoptions(threshold=20, precision=3, suppress=True, linewidth=200)

BALL_COLOR = (217, 79, 0)
BACKGROUND_COLOR = (60, 179, 113)
COIN_COLOR = (0, 125, 0)

GOAL_NET_COLOR = (143, 188, 143)

# game settings:
MATCH_MAX_TIME = 600  # 10 minutes de match
MATCH_MID_TIME = 300  # 5 minutes avant la fin de la première manche

WINDOW_WIDTH_ADULT_SIZE = 1600
WINDOW_HEIGHT_ADULT_SIZE = 1100

WINDOW_WIDTH_KID_SIZE = 1100
WINDOW_HEIGHT_KID_SIZE = 800

PLAYER_SPEED_X = 10 * 0.5
PLAYER_SPEED_Y = 10 * 0.5
MAX_BALL_SPEED = 15 * 1.5

TIMESTEP = 1 / 30.
NUDGE = 0.1
FRICTION = 0.95  # 1 means no FRICTION, less means FRICTION
INIT_DELAY_FRAMES = 30
# GRAVITY = -9.8 * 2 * 1.5

MAXPOINT = 5  # game ends when one agent loses this many games
# TODO: Adapter les valeurs pour qu'elles soient plus réelle
# TODO : Ajouter une fonction de calcul extérieur permettant la conversion entre
#        la puissance de tir et la vitesse en cm/sec ou m/s
SHOT_POWER = 6
# TODO : Ajouter une fonction de calcul extérieur permettant la conversion entre
#        la distance de tir et une distance en cm ou m

# la distance dépend de la taille de l'agent (kid size adult size)

SHOT_DISTANCE = 0.75

PLAYER_SPEED_FORWARD = 6.5 * 0.5
PLAYER_SPEED_BACKWARD = 6.5 * 0.5
PLAYER_SPEED_LEFT = 2
PLAYER_SPEED_RIGHT = PLAYER_SPEED_LEFT
