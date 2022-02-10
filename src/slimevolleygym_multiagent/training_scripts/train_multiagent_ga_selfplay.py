# Trains an agent from scratch (no existing AI) using evolution
# GA with no cross-over, just mutation, and random tournament selection
# Not optimized for speed, and just uses a single CPU (mainly for simplicity)

import os
import json
import numpy as np
import gym
import slimevolleygym.mlp as mlp
from slimevolleygym.mlp import Model
from slimevolleygym import multiagent_rollout as rollout
from lib import csvLib, jsonLib

# Settings
random_seed = 612
population_size = 128
total_tournaments = 5000
save_freq = 500
SETTINGS_FILE = "env.json"
RESULT_FILE = "results"
jsonIn = jsonLib.jsonInput('env.json')
csvOut = csvLib.CsvOutput(jsonIn.get_value_from_Json("ia_teams")[0], jsonIn.get_value_from_Json("ia_teams")[1], RESULT_FILE)

def mutate(length, mutation_rate, mutation_sigma):
  # (not used, in case I wanted to do partial mutations)
  # create an additive mutation vector of some size
  mask = np.random.randint(int(1/mutation_rate), size=length)
  mask = 1-np.minimum(mask, 1)
  noise = np.random.normal(size=length) * mutation_sigma
  return mask * noise

# Log results
logdir = "ga_selfplay"
if not os.path.exists(logdir):
  os.makedirs(logdir)


# Create two instances of a feed forward policy we may need later.
policy_left_train = Model(mlp.games['slimevolleymultiagent'])
policy_left_2 = Model(mlp.games['slimevolleymultiagent'])
policy_right_1 = Model(mlp.games['slimevolleymultiagent'])
policy_right_2 = Model(mlp.games['slimevolleymultiagent'])

param_count = policy_left_train.param_count
print("Number of parameters of the neural net policy:", param_count) # 273 for slimevolleylite

# store our population here
population = np.random.normal(size=(population_size, param_count)) * 0.5 # each row is an agent.
winning_streak = [0] * population_size # store the number of wins for this agent (including mutated ones)

# create the gym environment, and seed it
#env = gym.make("SlimeVolleyMultiAgentEnv")
env = gym.make(jsonIn.get_value_from_Json("id"),
               team_left_dict=jsonIn.get_value_from_Json("arguments", "team_left_dict"),
               team_right_dict=jsonIn.get_value_from_Json("arguments", "team_right_dict"))

env.seed(random_seed)
np.random.seed(random_seed)

history = []
for tournament in range(1, total_tournaments+1):

  m, n, o, p = np.random.choice(population_size, 4, replace=False)

  policy_left_train.set_model_params(population[m])
  policy_left_2.set_model_params(population[n])
  policy_right_1.set_model_params(population[o])
  policy_right_2.set_model_params(population[p])

  # the match between the mth and nth member of the population
  score, length = rollout(env, policy_right_1, policy_right_2, policy_left_train, policy_left_2)

  history.append(length)
  # if score is positive, it means policy_right won.
  if score == 0: # if the game is tied, add noise to the left agent.
    population[m] += np.random.normal(size=param_count) * 0.1
    population[n] += np.random.normal(size=param_count) * 0.1
  if score > 0:
    population[m] = population[o] + np.random.normal(size=param_count) * 0.1
    population[n] = population[p] + np.random.normal(size=param_count) * 0.1
    winning_streak[m] = winning_streak[o]
    winning_streak[o] += 1
    winning_streak[n] = winning_streak[p]
    winning_streak[p] += 1
  if score < 0:
    population[o] = population[m] + np.random.normal(size=param_count) * 0.1
    population[p] = population[n] + np.random.normal(size=param_count) * 0.1
    winning_streak[o] = winning_streak[m]
    winning_streak[m] += 1
    winning_streak[p] = winning_streak[n]
    winning_streak[n] += 1

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