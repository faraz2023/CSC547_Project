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
    
    def __init__(self, burgers, u_max, f_max, nu, eps, u_star):
        self.burgers = burgers
        self.u_max = u_max
        self.f_max = f_max
        self.n_x = self.burgers.NX
        self.x_max  = self.burgers.XMAX
        self.nu = nu
        self.eps = eps
        self.u_star = u_star 
        self.viewer = None
        
    
        f_high = np.full((self.n_x), self.f_max, dtype = np.float32)
        u_high = np.full((self.n_x), self.u_max, dtype = np.float32)
        self.action_space = spaces.Box(
            low=-f_high,
            high=f_high,
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

    def step(self, f, t_start, t_end):
        u = self.state 

        # f = np.clip(f, -self.f_max, self.f_max)
        
        # costs = np.sum((u[:, -1] - self.u_star)**2)
        # costs = np.sum((u[:, -1] - self.u_star)**2)
        
        du = utils.differentiate(u[:,-1], self.x_max, self.n_x)
        costs = np.sum((du)**2)

        self.state = self.burgers.convection_diffusion(t_start, t_end, self.nu, self.eps, u, f)
        

        return self.state[:, -1], du, -costs, False, {}

    def reset(self):
        self.state = self.burgers.InitialCondition(self.nu) 
        self.last_u = None
        return self.state[:, 0]