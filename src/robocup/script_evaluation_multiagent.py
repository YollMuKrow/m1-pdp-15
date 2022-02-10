import warnings

# numpy warnings because of tensorflow
warnings.filterwarnings("ignore", category=FutureWarning, module='tensorflow')
warnings.filterwarnings("ignore", category=UserWarning, module='gym')

import gym
import os
import numpy as np
import argparse
import robocup
from model.mlp import makeRoboCupAdultSizePolicy  # model de jeu
from time import sleep
from lib import csvLib, jsonLib

SETTINGS_FILE = "robocup/spec/env_eval.json"
RESULT_FILE = "results"
JSON = jsonLib.jsonInput(SETTINGS_FILE)
csvOut = csvLib.CsvOutput(JSON.get_value_from_Json("ia_teams")[0], JSON.get_value_from_Json("ia_teams")[1], RESULT_FILE)

np.set_printoptions(threshold=20, precision=4, suppress=True, linewidth=200)


class RandomPolicy:
    def __init__(self, path):
        self.action_space = gym.spaces.MultiBinary(7)  # action aléatoire pour les 7 actions disponible par agent
        pass

    def predict(self, obs):
        return self.action_space.sample()


def rollout(env, policy_left, policy_right, render_mode=False):
    """ play 2 agent vs 2 other agent in modified robocup game loop. """
    # same observation at the very beginning for all agent
    obs0 = env.reset()
    list_obs = []
    for obs_ite in range(len(policy_left) + len(policy_right) - 1):
        list_obs.append(obs0)

    done = False
    total_reward = 0

    while not done:
        # TODO : Faire une version plus adaptative en fonction du nombre de joueur
        # right team
        action0 = policy_right[0].predict(obs0)     # pink
        action1 = policy_right[1].predict(list_obs[0])  #white
        # left team
        action2 = policy_left[0].predict(list_obs[1])   #yellow
        action3 = policy_left[1].predict(list_obs[2])   #green

        # add to each agent his observation
        obs0, reward, done, info = env.step(action2, action3, action0, action1)

        team_left_color_num_action_dict = JSON.get_value_from_Json('arguments', 'team_left_color_num_action_dict')
        team_right_color_num_action_dict = JSON.get_value_from_Json('arguments', 'team_right_color_num_action_dict')
        all_agent = {**team_right_color_num_action_dict, **team_left_color_num_action_dict}
        action_iterate = 0

        for agent in all_agent:
            if agent in info:
                list_obs[action_iterate] = info[agent]
        total_reward += reward

        if render_mode:
            env.render()
            sleep(0.01)

    return total_reward


def evaluate_multiagent(env, policy_left, policy_right, render_mode=False, n_trials=1000, init_seed=721):
    history = []
    for i in range(n_trials):
        env.seed(seed=init_seed + i)
        cumulative_score = rollout(env, policy_left, policy_right, render_mode=render_mode)
        print("cumulative score #", i, ":", cumulative_score)
        history.append(cumulative_score)
    return history


if __name__ == "__main__":

    APPROVED_MODELS = ["ga", "random"]


    def checkchoice(choice):
        choice = choice.lower()
        if choice not in APPROVED_MODELS:
            return False
        return True


    PATH = {
        "ga": "training_scripts/ga_selfplay/ga_res.json",
        "random": None,
    }

    MODEL = {
        "ga": makeRoboCupAdultSizePolicy,
        "random": RandomPolicy,
    }

    env = gym.make(JSON.get_value_from_Json('id'), team_left_color_num_action_dict=JSON.get_value_from_Json(
        'arguments', 'team_left_color_num_action_dict'), team_right_color_num_action_dict=JSON.get_value_from_Json(
        'arguments', 'team_right_color_num_action_dict'), configuration=JSON.get_value_from_Json("configuration"))

    env.seed(JSON.get_value_from_Json('arguments', 'seed'))

    render_mode = JSON.get_value_from_Json('arguments', 'render') == 1

    assert checkchoice(JSON.get_value_from_Json("ia_teams")[0])  # args.right), "pls enter a valid agent"
    assert checkchoice(JSON.get_value_from_Json("ia_teams")[1]), "pls enter a valid agent"

    c0 = JSON.get_value_from_Json("ia_teams")[0]
    c1 = JSON.get_value_from_Json("ia_teams")[1]

    path0 = PATH[c0]
    path1 = PATH[c1]

    if len(JSON.get_value_from_Json('arguments', 'right_path')) > 0:
        assert os.path.exists(JSON.get_value_from_Json('arguments', 'right_path')), JSON.get_value_from_Json(
            'arguments', 'right_path') + " doesn't exist."
        path0 = JSON.get_value_from_Json('arguments', 'right_path')
        print("path of right model", path0)

    if len(JSON.get_value_from_Json('arguments', 'left_path')):
        assert os.path.exists(JSON.get_value_from_Json('arguments', 'left_path')), JSON.get_value_from_Json('arguments',
                                                                                                            'left_path') + " doesn't exist."
        path1 = JSON.get_value_from_Json('arguments', 'left_path')
        print("path of left model", path1)

    team_left = JSON.get_value_from_Json(
        'arguments', 'team_left_color_num_action_dict')
    team_right = JSON.get_value_from_Json(
        'arguments', 'team_right_color_num_action_dict')

    policy_left = []
    policy_right = []

    for nb_policy in range(len(team_right)):
        policy_right.append(MODEL[c0](path0))
    for nb_policy in range(len(team_left)):
        policy_left.append(MODEL[c1](path1))

    history = evaluate_multiagent(env, policy_left, policy_right,
                                  render_mode=render_mode, n_trials=JSON.get_value_from_Json('arguments', 'trials'),
                                  init_seed=JSON.get_value_from_Json('arguments', 'seed'))

    print("history dump:", history)
    print(c0 + " scored", np.round(np.mean(history), 7), "±", np.round(np.std(history), 7), "vs",
          c1, "over", JSON.get_value_from_Json('arguments', 'trials'), "trials.")
    csvOut.write_result(np.round(np.mean(history), 7))
