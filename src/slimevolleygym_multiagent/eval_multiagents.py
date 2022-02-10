import warnings
# numpy warnings because of tensorflow
warnings.filterwarnings("ignore", category=FutureWarning, module='tensorflow')
warnings.filterwarnings("ignore", category=UserWarning, module='gym')

import gym
import os
import numpy as np
import argparse
import slimevolleygym
from slimevolleygym.mlp import makeSlimePolicy, makeSlimePolicyLite, makeSlimePolicyMultiAgent # simple pretrained models
from time import sleep
from lib import csvLib, jsonLib
#import cv2


SETTINGS_FILE = "env.json"
RESULT_FILE = "results"
jsonIn = jsonLib.jsonInput('env.json')
csvOut = csvLib.CsvOutput(jsonIn.get_value_from_Json("ia_teams")[0], jsonIn.get_value_from_Json("ia_teams")[1], RESULT_FILE)

np.set_printoptions(threshold=20, precision=4, suppress=True, linewidth=200)

class RandomPolicy:
  def __init__(self, path):
    self.action_space = gym.spaces.MultiBinary(3)
    pass
  def predict(self, obs):
    return self.action_space.sample()

def rollout(env, policy0, policy1, policy2, policy3, render_mode=False):
  """ play 2 agent vs the other in modified gym-style loop. """
  obs0 = env.reset()
  obs1 = obs0 # same observation at the very beginning for the other agent
  obs2 = obs0 # same observation at the very beginning for the other agent
  obs3 = obs0 # same observation at the very beginning for the other agent

  done = False
  total_reward = 0
  #count = 0

  while not done:

    #right
    action0 = policy0.predict(obs0)
    action1 = policy1.predict(obs1)
    #left
    action2 = policy2.predict(obs2)
    action3 = policy3.predict(obs3)

    # uses a 2nd (optional) parameter for step to put in the other action
    # and returns the other observation in the 4th optional "info" param in gym's step()
    all_actions = [action2, action3, action0, action1]
    obs0, reward, done, info = env.step(all_actions)
    obs1 = info['otherAllyState']
    obs2 = info['otherObs']
    obs3 = info['otherEnnemyState']

    total_reward += reward

    if render_mode:
      env.render()
      sleep(0.01)

  return total_reward

def evaluate_multiagent(env, policy0, policy1, policy2, policy3, render_mode=False, n_trials=1000, init_seed=721):
  history = []
  for i in range(n_trials):
    env.seed(seed=init_seed+i)
    cumulative_score = rollout(env, policy0, policy1, policy2, policy3, render_mode=render_mode)
    print("cumulative score #", i, ":", cumulative_score)
    history.append(cumulative_score)
  return history

if __name__=="__main__":

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
    "ga": makeSlimePolicyMultiAgent,
    "random": RandomPolicy,
  }

  parser = argparse.ArgumentParser(description='Evaluate pre-trained agents against each other.')
  parser.add_argument('--left', help='choice of (baseline, ppo, cma, ga, random)', type=str, default="ga")
  parser.add_argument('--leftpath', help='path to left model (leave blank for zoo)', type=str, default="")
  parser.add_argument('--right', help='choice of (baseline, ppo, cma, ga, random)', type=str, default="random")
  parser.add_argument('--rightpath', help='path to right model (leave blank for zoo)', type=str, default="")
  parser.add_argument('--render', action='store_true', help='render to screen?', default=False)
  parser.add_argument('--seed', help='random seed (integer)', type=int, default=721)
  parser.add_argument('--trials', help='number of trials (default 1000)', type=int, default=1000)

  args = parser.parse_args()

  #env = gym.make("SlimeVolley-v0")
  env = gym.make(jsonIn.get_value_from_Json("id"),
                 team_left_dict=jsonIn.get_value_from_Json("arguments", "team_left_dict"),
                 team_right_dict=jsonIn.get_value_from_Json("arguments", "team_right_dict"))
  env.seed(args.seed)

  render_mode = args.render

  assert checkchoice(args.right), "pls enter a valid agent"
  assert checkchoice(args.left), "pls enter a valid agent"

  c0 = args.right
  c1 = args.left

  path0 = PATH[c0]
  path1 = PATH[c1]

  if len(args.rightpath) > 0:
    assert os.path.exists(args.rightpath), args.rightpath+" doesn't exist."
    path0 = args.rightpath
    print("path of right model", path0)

  if len(args.leftpath):
    assert os.path.exists(args.leftpath), args.leftpath+" doesn't exist."
    path1 = args.leftpath
    print("path of left model", path1)

  policy0 = MODEL[c0](path0) # the right agent 1
  policy1 = MODEL[c0](path0) # the right agent 2
  policy2 = MODEL[c1](path1) # the left agent 3
  policy3 = MODEL[c1](path1) # the left agent 4

  history = evaluate_multiagent(env, policy0, policy1, policy2, policy3,
    render_mode=render_mode, n_trials=args.trials, init_seed=args.seed)

  print("history dump:", history)
  print(c0+" scored", np.round(np.mean(history), 3), "±", np.round(np.std(history), 3), "vs",
    c1, "over", args.trials, "trials.")
