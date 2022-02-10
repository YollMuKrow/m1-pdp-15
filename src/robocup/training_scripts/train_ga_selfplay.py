# Trains an agent from scratch (no existing AI) using evolution
# GA with no cross-over, just mutation, and random tournament selection
# Not optimized for speed, and just uses a single CPU (mainly for simplicity)

import os
import json
import numpy as np
import gym

from model import mlp
from model.mlp import Model
from robocup.helper import multiagent_rollout as rollout

# Settings
random_seed = 612
population_size = 128
total_tournaments = 5000
save_freq = 500

# Log results
logdir = "ga_selfplay"
if not os.path.exists(logdir):
  os.makedirs(logdir)


# Create two instances of a feed forward policy we may need later.
dict_team_agent_being_trained = {'yellow': Model(mlp.games['robocup_adult_size']), 'green': Model(mlp.games['robocup_adult_size'])}
dict_other_team = {'pink': Model(mlp.games['robocup_adult_size']), 'white': Model(mlp.games['robocup_adult_size'])}

param_count = dict_team_agent_being_trained['yellow'].param_count
print("Number of parameters of the neural net policy:", param_count) # 273 for slimevolleylite

# store our population here
population = np.random.normal(size=(population_size, param_count)) * 0.5 # each row is an agent.
winning_streak = [0] * population_size # store the number of wins for this agent

# create the gym environment, and seed it
env = gym.make('RoboCupAdultSize-v0', team_left_color_num_action_dict={"yellow": 0, "green": 1},
               team_right_color_num_action_dict={"pink": 2, "white": 3}, configuration=[])

env.seed(random_seed)
np.random.seed(random_seed)

history = []
for tournament in range(1, total_tournaments+1):

  m, n, o, p = np.random.choice(population_size, 4, replace=False)

  dict_team_agent_being_trained['yellow'].set_model_params(population[m])
  dict_team_agent_being_trained['green'].set_model_params(population[n])

  dict_other_team['pink'].set_model_params(population[o])
  dict_other_team['white'].set_model_params(population[p])

  # the match between the mth and nth member of the population
  score, length = rollout(env, 'yellow', dict_team_agent_being_trained['yellow'], 'green', dict_team_agent_being_trained['green'],
                          'pink', dict_other_team['pink'], 'white', dict_other_team['white'])

  history.append(length)
  # if score is positive, it means policy_right won.
  if score == 0: # if the game is tied, add noise to the left agent.
    population[o] += np.random.normal(size=param_count) * 0.1
    population[p] += np.random.normal(size=param_count) * 0.1

  if score > 0:
    population[o] = population[m] + np.random.normal(size=param_count) * 0.1
    winning_streak[o] = winning_streak[m]
    winning_streak[m] += 1
    population[p] = population[n] + np.random.normal(size=param_count) * 0.1
    winning_streak[p] = winning_streak[n]
    winning_streak[n] += 1

  if score < 0:
    population[m] = population[o] + np.random.normal(size=param_count) * 0.1
    winning_streak[m] = winning_streak[o]
    winning_streak[o] += 1
    population[n] = population[p] + np.random.normal(size=param_count) * 0.1
    winning_streak[n] = winning_streak[p]
    winning_streak[p] += 1

  if tournament % save_freq == 0:
    model_filename = os.path.join(logdir, "ga_"+str(tournament).zfill(8)+".json")
    with open(model_filename, 'wt') as out:
      record_holder = np.argmax(winning_streak)
      record = winning_streak[record_holder]
      json.dump([population[record_holder].tolist(), record], out, sort_keys=True, indent=0, separators=(',', ': '))

  if (tournament ) % 100 == 0:
    record_holder = np.argmax(winning_streak)
    record = winning_streak[record_holder]
    print("tournament:", tournament,
          "best_winning_streak:", record,
          "mean_duration", np.mean(history),
          "stdev:", np.std(history),
         )
    history = []