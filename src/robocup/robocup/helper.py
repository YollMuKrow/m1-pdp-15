#####################
# helper functions: #
#####################
from typing import Dict, Tuple

from model.mlp import Model


def multiagent_rollout(env, agent_0_color: str, agent_0_policy: Model, agent_1_color: str, agent_1_policy: Model,
                       agent_2_color: str, agent_2_policy: Model, agent_3_color: str, agent_3_policy: Model,
                       render_mode=False):
    obs_agent_0 = env.reset()

    # à modifier

    obs_agent_1 = obs_agent_0
    obs_agent_2 = obs_agent_0
    obs_agent_3 = obs_agent_0

    done = False
    total_reward = 0
    t = 0

    while not done:

        # Agent qu'on entraine
        action_0 = agent_0_policy.predict(obs_agent_0)

        # Agent allié + agent ennemi
        action_1 = agent_1_policy.predict(obs_agent_1)
        action_2 = agent_2_policy.predict(obs_agent_2)
        action_3 = agent_3_policy.predict(obs_agent_3)

        # uses a 2nd (optional) parameter for step to put in the other action
        # and returns the other observation in the 4th optional "info" param in gym's step()
        obs_agent_0, reward, done, info = env.step(action_0, action_1, action_2, action_3)

        obs_agent_1 = info[agent_1_color]
        obs_agent_2 = info[agent_2_color]
        obs_agent_3 = info[agent_3_color]

        total_reward += reward
        t += 1

        if render_mode:
            env.render()
    return total_reward, t
