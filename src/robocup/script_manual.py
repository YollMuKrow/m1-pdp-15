"""
State mode (Optional Human vs Built-in AI)

FPS (no-render): 100000 steps /7.956 seconds. 12.5K/s.
"""

import numpy as np
import gym
import robocup
from lib import jsonLib, csvLib

np.set_printoptions(threshold=20, precision=3, suppress=True, linewidth=200)

# game settings:
RESULT_FILE = "results_manual"
JSON = jsonLib.jsonInput("robocup/spec/env.json")
csvOut = csvLib.CsvOutput(JSON.get_value_from_Json("ia_teams")[0], JSON.get_value_from_Json("ia_teams")[1], RESULT_FILE)
RENDER_MODE = True

if __name__ == "__main__":
    if RENDER_MODE:
        from pyglet.window import key
        from time import sleep

    agent1_manual_action = [0, 0, 0, 0, 0, 0, 0]  # left, right, forward, backward, shoot, rotate_left, rotate_right
    agent2_manual_action = [0, 0, 0, 0, 0, 0, 0]
    agent3_manual_action = [0, 0, 0, 0, 0, 0, 0]
    agent4_manual_action = [0, 0, 0, 0, 0, 0, 0]

    agent1_manual_mode = False
    agent2_manual_mode = False
    agent3_manual_mode = False
    agent4_manual_mode = False

    STOP = False


    def key_press(k, mod):
        global agent1_manual_mode, agent1_manual_action, agent2_manual_mode, agent2_manual_action, agent3_manual_mode, agent3_manual_action, agent4_manual_mode, agent4_manual_action, STOP

        # agent1
        if k == key.D:  agent1_manual_action[0] = 1
        if k == key.Q: agent1_manual_action[1] = 1
        if k == key.S:    agent1_manual_action[2] = 1
        if k == key.Z:  agent1_manual_action[3] = 1
        if k == key.W:     agent1_manual_action[4] = 1
        if k == key.A: agent1_manual_action[5] = 1
        if k == key.E: agent1_manual_action[6] = 1
        if (k == key.Q or k == key.D or k == key.Z or k == key.S or
                k == key.W or k == key.A or k == key.E): agent1_manual_mode = True

        # agent2
        if k == key.H:     agent2_manual_action[0] = 1
        if k == key.F:     agent2_manual_action[1] = 1
        if k == key.G:     agent2_manual_action[2] = 1
        if k == key.T:     agent2_manual_action[3] = 1
        if k == key.C: agent2_manual_action[4] = 1
        if k == key.R: agent2_manual_action[5] = 1
        if k == key.Y: agent2_manual_action[6] = 1
        if (k == key.F or k == key.H or k == key.T or k == key.G or
                k == key.C or k == key.R or k == key.Y): agent2_manual_mode = True

        # agent3
        if k == key.J:     agent3_manual_action[0] = 1
        if k == key.L:     agent3_manual_action[1] = 1
        if k == key.I:     agent3_manual_action[2] = 1
        if k == key.K:     agent3_manual_action[3] = 1
        if k == key.N: agent3_manual_action[4] = 1
        if k == key.U: agent3_manual_action[5] = 1
        if k == key.O: agent3_manual_action[6] = 1
        if (k == key.J or k == key.L or k == key.I or k == key.K or
                k == key.N or k == key.U or k == key.O): agent3_manual_mode = True

        # agent4
        if k == key.LEFT:     agent4_manual_action[0] = 1
        if k == key.RIGHT:     agent4_manual_action[1] = 1
        if k == key.UP:     agent4_manual_action[2] = 1
        if k == key.DOWN:     agent4_manual_action[3] = 1
        if k == key.SPACE: agent4_manual_action[4] = 1
        if k == key.NUM_1: agent4_manual_action[5] = 1
        if k == key.NUM_3: agent4_manual_action[6] = 1
        if (k == key.LEFT or k == key.RIGHT or k == key.UP or
                k == key.DOWN or k == key.SPACE or k == key.NUM_1 or k == key.NUM_3): agent4_manual_mode = True

        # STOP

        if k == key.ESCAPE: STOP = True


    def key_release(k, mod):
        global agent1_manual_mode, agent1_manual_action, agent2_manual_mode, agent2_manual_action, agent3_manual_mode, agent3_manual_action, agent4_manual_mode, agent4_manual_action, STOP

        # agent1
        if k == key.D:  agent1_manual_action[0] = 0
        if k == key.Q: agent1_manual_action[1] = 0
        if k == key.S:    agent1_manual_action[2] = 0
        if k == key.Z:  agent1_manual_action[3] = 0
        if k == key.W:     agent1_manual_action[4] = 0
        if k == key.A: agent1_manual_action[5] = 0
        if k == key.E: agent1_manual_action[6] = 0

        # agent2
        if k == key.H:     agent2_manual_action[0] = 0
        if k == key.F:     agent2_manual_action[1] = 0
        if k == key.G:     agent2_manual_action[2] = 0
        if k == key.T:     agent2_manual_action[3] = 0
        if k == key.C: agent2_manual_action[4] = 0
        if k == key.R: agent2_manual_action[5] = 0
        if k == key.Y: agent2_manual_action[6] = 0

        # agent3
        if k == key.J:     agent3_manual_action[0] = 0
        if k == key.L:     agent3_manual_action[1] = 0
        if k == key.I:     agent3_manual_action[2] = 0
        if k == key.K:     agent3_manual_action[3] = 0
        if k == key.N: agent3_manual_action[4] = 0
        if k == key.U: agent3_manual_action[5] = 0
        if k == key.O: agent3_manual_action[6] = 0

        # agent4
        if k == key.LEFT:     agent4_manual_action[0] = 0
        if k == key.RIGHT:     agent4_manual_action[1] = 0
        if k == key.UP:     agent4_manual_action[2] = 0
        if k == key.DOWN:     agent4_manual_action[3] = 0
        if k == key.SPACE: agent4_manual_action[4] = 0
        if k == key.NUM_1: agent4_manual_action[5] = 0
        if k == key.NUM_3: agent4_manual_action[6] = 0

        # STOP

        if k == key.ESCAPE: STOP = False

    # 'RoboCupAdultSize-v0' ou 'RoboCupKidSize-v0'
    # configuration : -> chaine de caractère
    # 'collision_disable'
    # 'allies_vision_disable'
    # 'opponents_vision_disable'

    # exemple: configuration=['collision_disable', 'allies_vision_disable']

    env = gym.make(JSON.get_value_from_Json('id'), team_left_color_num_action_dict=JSON.get_value_from_Json(
        'arguments', 'team_left_color_num_action_dict'), team_right_color_num_action_dict=JSON.get_value_from_Json(
        'arguments', 'team_right_color_num_action_dict'), configuration=JSON.get_value_from_Json("configuration"))

    env.seed(np.random.randint(0, 10000))
    # env.seed(689)

    if RENDER_MODE:
        env.render()
        env.viewer.window.on_key_press = key_press
        env.viewer.window.on_key_release = key_release

    obs = env.reset()

    steps = 0
    total_reward = 0
    action1 = np.array([0, 0, 0, 0, 0, 0, 0])

    #print(obs)

    done = False

    while not done and not STOP:

        if agent1_manual_mode:  # override with keyboard
            action1 = agent1_manual_action
        else:
            action1 = np.array([0, 0, 0, 0, 0, 0, 0])

        if agent2_manual_mode:
            action2 = agent2_manual_action
        else:
            action2 = np.array([0, 0, 0, 0, 0, 0, 0])

        if agent3_manual_mode:
            action3 = agent3_manual_action
        else:
            action3 = np.array([0, 0, 0, 0, 0, 0, 0])

        if agent4_manual_mode:
            action4 = agent4_manual_action
        else:
            action4 = np.array([0, 0, 0, 0, 0, 0, 0])

        obs, reward, done, info = env.step(action1, action2, action3, action4)

        if STOP:
            break

        if reward > 0 or reward < 0:
            agent1_manual_mode = False
            agent2_manual_mode = False
            agent3_manual_mode = False
            agent4_manual_mode = False

        total_reward += reward

        if RENDER_MODE:
            env.render()
            sleep(0.02)  # 0.01

        #print(info)
        #print('\n')

    env.close()
    csvOut.write_result(total_reward)
    print("cumulative score", total_reward)
