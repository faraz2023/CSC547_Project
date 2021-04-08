import gym
from gym import spaces
from gym.utils import seeding
import numpy as np
from os import path
import utils


class SpdeEnv(gym.Env):
    metadata = {
        'render.modes': ['human', 'rgb_array'],
        'video.frames_per_second': 30
    }
    
    @staticmethod
    def sigmoid(x):
        return 1/(1 + np.exp(-x))

    def function_theta(self, theta):
        a = np.arange(self.n_x, dtype = np.float32)
        f = np.tanh(theta[0] * a + theta[1]) * theta[2] + theta[3]
        return f - np.average(f)
    
    def __init__(self, burgers, u_max, f_max, theta_high, theta_size, nu, eps, u_star, lambda1 = 0.05):
        self.burgers = burgers
        self.u_max = u_max
        self.theta_high = theta_high
        self.f_max = f_max
        self.n_x = self.burgers.NX
        self.x_max  = self.burgers.XMAX
        self.nu = nu
        self.eps = eps
        self.u_star = u_star 
        self.viewer = None
        self.lambda1 = lambda1
        self.theta_size = theta_size
        
  
        u_high = np.full((self.n_x), self.u_max, dtype = np.float32)
        # f_high = np.full((self.n_x), self.f_max, dtype = np.float32)

        self.action_space = spaces.Box(
            low=-theta_high,
            high=theta_high,
            dtype=np.float32
        )
        self.observation_space = spaces.Box(
            low=-u_high,
            high=u_high,
            dtype=np.float32
        )

        self.seed()

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def step(self, theta, t_start, t_end, prev_condition):

        theta = np.clip(theta, -self.theta_high, self.theta_high)
        f = self.function_theta(theta)
        f = np.clip(f, -self.f_max, self.f_max)
        
        u = self.burgers.convection_diffusion(t_start, t_end, self.nu, self.eps, prev_condition, f)
        self.state = u
        # costs = np.sum((u[:, -1] - self.u_star)**2)
        # costs = np.sum((u[:, -1] - self.u_star)**2)
        du = utils.differentiate(u[:,-1], self.x_max, self.n_x)
        
        regularizer = self.lambda1 * np.average((f[1:] - f[:-1])**2)
        u_avg  = np.average(u[:,-1])
        costs = np.average((u[:, -1] -  u_avg)**2)
        # costs += regularizer
        # costs = np.max(u[:,-1]) - np.min(u[:,-1])

        return self.state[:, -1], du, -costs, False, {}

    def reset(self):
        self.state = self.burgers.u 
        self.state[:, 0] = self.burgers.InitialCondition(self.nu) 
        self.last_u = None
        return self.state[:, 0]
