import matplotlib.pyplot as plt 
import numpy as np
from SpdeEnv import SpdeEnv
from SPDEs import Burgers
from math import pi as PI
from utils import make_dir
from utils import plotLearning
from model import Agent
import os
import time
from datetime import datetime


NT = 301
T_START = 0
T_END = 1
NX = 151
XMAX = 2.0*PI
NU = 0.01
EPS = 0.01
seed  = 0
lambda1 = 0.2
theta_2_scale = 1

burgers = Burgers(XMAX, NX, NT)
UMAX = 8
USTAR = np.full(NX, 4.0, dtype = np.float32)
#THETAHIGH = np.array([1, 150, 1, 1], dtype = np.float32)
#THETASIZE = 4
F_MAX = 5

env = SpdeEnv(burgers, UMAX, F_MAX, NU, EPS, USTAR, lambda1)
chkpt_dir = 'experiment_out'
make_dir(chkpt_dir)

agent = Agent(alpha=0.000025, beta=0.00025, input_dims=[NX], tau=0.1, env=env,
              batch_size=64,  layer1_size=400, layer2_size=300, n_actions= NX, chkpt_dir=chkpt_dir)

np.random.seed(seed)

make_dir('logs')
now = datetime.now()
current_time = now.strftime("%H:%M:%S")
log_dir_name = "./logs/{}".format(current_time)
os.mkdir(log_dir_name)

score_history = []
num_episodes = 100
episode_length = 10
for j in range(num_episodes):
    obs = env.reset()
    done = False
    score = 0

    now = datetime.now()
    iter_log_dir_name = "{}/{}".format(log_dir_name, j)
    os.mkdir(iter_log_dir_name)
    for i in range(episode_length):
        T_START = i 
        T_END = (i + 1) 
        act = agent.choose_action(obs).astype('double')
        #act[1] *= theta_2_scale 
        # if i % 10 == 0:
        #     print(act)
        idx = np.argmax(obs)

        #plt.plot(env.function_theta(act))
        plt.plot(act)
        plt.savefig("{}/{}-act.png".format(iter_log_dir_name, i))
        plt.close()

        # print("-----")
        # print("1: {}".format(act[idx]))
        # print("2: {}".format(np.average(act)))
        new_state, derivaties, reward, done, info = env.step(act, T_START, T_END)
      

        agent.remember(obs, act, reward, new_state, int(done))
        agent.learn()
        score += reward
        obs = new_state

        #env.render()
    score_history.append(score / episode_length)

    #if i % 25 == 0:
    #    agent.save_models()

    print('episode ', j, 'score %.2f' % score,
          'trailing 100 games avg %.3f' % np.mean(score_history[-100:]))

filename = 'LunarLander-alpha000025-beta00025-400-300.png'
plotLearning(score_history, filename, window=100)
