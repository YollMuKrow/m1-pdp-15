"""
State mode (Optional Human vs Built-in AI)

FPS (no-render): 100000 steps /7.956 seconds. 12.5K/s.
"""

import math
import numpy as np
import gym
import slimevolleygym
from lib import *
from lib import csvLib, jsonLib

np.set_printoptions(threshold=20, precision=3, suppress=True, linewidth=200)

# game settings:

RENDER_MODE = True
SETTINGS_FILE = "env.json"
RESULT_FILE = "results"
jsonIn = jsonLib.jsonInput('env.json')
csvOut = csvLib.CsvOutput(jsonIn.get_value_from_Json("ia_teams")[0], jsonIn.get_value_from_Json("ia_teams")[1],
                          RESULT_FILE)

if __name__ == "__main__":
    """
  Example of how to use Gym env, in single or multiplayer setting

  Humans can override controls:

  blue Agent:
  Z - Jump
  Q - Left
  D - Right

  Yellow Agent:
  Up Arrow, Left Arrow, Right Arrow
  """

    if RENDER_MODE:
        from pyglet.window import key
        from time import sleep

    manualAction = [0, 0, 0]  # forward, backward, jump
    otherManualAction = [0, 0, 0]
    manualMode = False
    otherManualMode = False


    # taken from https://github.com/openai/gym/blob/master/gym/envs/box2d/car_racing.py
    def key_press(k, mod):
        global manualMode, manualAction, otherManualMode, otherManualAction
        if k == key.LEFT:  manualAction[0] = 1
        if k == key.RIGHT: manualAction[1] = 1
        if k == key.UP:    manualAction[2] = 1
        if (k == key.LEFT or k == key.RIGHT or k == key.UP): manualMode = True

        if k == key.D:     otherManualAction[0] = 1
        if k == key.Q:     otherManualAction[1] = 1
        if k == key.Z:     otherManualAction[2] = 1
        if (k == key.D or k == key.Q or k == key.Z): otherManualMode = True


    def key_release(k, mod):
        global manualMode, manualAction, otherManualMode, otherManualAction
        if k == key.LEFT:  manualAction[0] = 0
        if k == key.RIGHT: manualAction[1] = 0
        if k == key.UP:    manualAction[2] = 0
        if k == key.D:     otherManualAction[0] = 0
        if k == key.Q:     otherManualAction[1] = 0
        if k == key.Z:     otherManualAction[2] = 0


    ### TODO : load l'ia depuis le json
    policy = slimevolleygym.RandomPolicy()  # defaults to use RNN Baseline for player

    # on peut choisir le placement des joueurs (couleur) dans chacune des équipes
    # 'yellow' : 1 le joueur yellow récupère la deuxième action dans step(action1, action_2, action_3, action_4)
    # 'white' : 0 le joueur avec la première action dans step est celui qu'on entraîne (compatibilité gym)
    # indices de 0 à 4, pour les couleurs se référer au slimevolley.py COLOR

    env = gym.make(jsonIn.get_value_from_Json("id"),
                   team_left_dict=jsonIn.get_value_from_Json("arguments", "team_left_dict"),
                   team_right_dict=jsonIn.get_value_from_Json("arguments", "team_right_dict"))
    env.seed(np.random.randint(0, 10000))
    # env.seed(689)

    if RENDER_MODE:
        env.render()
        env.viewer.window.on_key_press = key_press
        env.viewer.window.on_key_release = key_release

    obs = env.reset()

    steps = 0
    total_reward = 0
    action = np.array([0, 0, 0])

    done = False

    while not done:

        if manualMode:  # override with keyboard
            action = manualAction
        else:
            action = policy.predict()

        if otherManualMode:
            otherAction = otherManualAction
            obs, reward, done, _ = env.step(action, otherAction)
        else:
            obs, reward, done, _ = env.step(action)

        if reward > 0 or reward < 0:
            manualMode = False
            otherManualMode = False

        total_reward += reward

        if RENDER_MODE:
            env.render()
            sleep(0.02)  # 0.01

    env.close()
    csvOut.write_result(total_reward)
    print('cumulative score', total_reward)
