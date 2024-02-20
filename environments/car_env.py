import numpy as np
import pygame

import gymnasium as gym
from gymnasium import spaces


class F1_Env(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}

    def __init__(self, size=(1920, 1080), map_path="./tracks/track01.png", render_mode=None):
        self.map_path = map_path
        self.size = size
        self.window_size = (512, 512)

        self.observation_space = spaces.Dict(
            {
                "agent": spaces.Box(low=np.array([0, 0]), high=np.array([size[0] - 1, size[1] - 1]), dtype=np.int64),
                "target": spaces.Box(low=np.array([0, 0]), high=np.array([size[0] - 1, size[1] - 1]), dtype=np.int64),
            }
        )

        # We have 4 actions, corresponding to "forward", "backwards", "left", "right"
        self.action_space = spaces.Discrete(4)

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

        self.window = None
        self.clock = None
