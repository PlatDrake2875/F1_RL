import sys
import pygame as pg
from pygame.locals import *
import numpy as np
from car import Car
from track import Track
import neat
import math
import time
import pickle
import random
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
import sys
import random
from tqdm import trange
import datetime
import gym
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt
import pickle
import seaborn as sns
import pandas as pd
from random import random
from datetime import datetime


class CarAgent(Car):
    def __init__(self, car_sprite, pos_x, pos_y, angle, speed, game_map, border_color,
                 map_width, map_height, top_start_point, bottom_start_point,
                 gamma=0.9, alpha=0.1, start_epsilon=1, end_epsilon=0.001, epsilon_decay=0.999):
        super().__init__(car_sprite, pos_x, pos_y, angle, speed, game_map, border_color,
                         map_width, map_height, top_start_point, bottom_start_point)

        self.n_action = 5
        self.gamma = gamma
        self.alpha = alpha

        # action values
        self.q = defaultdict(lambda: np.zeros(self.n_action))  # action value

        # epsilon greedy parameters
        self.start_epsilon = start_epsilon
        self.end_epsilon = end_epsilon
        self.epsilon_decay = epsilon_decay

    # get epsilon
    def get_epsilon(self, n_episode):
        epsilon = max(self.start_epsilon * (self.epsilon_decay ** n_episode), self.end_epsilon)
        return (epsilon)

    # select action based on epsilon greedy
    def select_action(self, state, epsilon):
        # implicit policy; if we have action values for that state, choose the largest one, else random
        best_action = np.argmax(self.q[state]) if state in self.q else np.random.randint(0, 4)
        if np.random.rand() < epsilon:
            action = np.random.randint(0, 4)
        else:
            action = best_action
        return (action)

    # Given (state, action, reward, next_state) pair after a transition made in the environment and the episode index
    def updateExperience(self, state, action, reward, next_state):
        best_actionIndex_fromNextState = np.argmax(self.q[next_state])
        best_actionValue_fromNextState = self.q[next_state][best_actionIndex_fromNextState]

        target = reward + self.gamma * best_actionValue_fromNextState
        self.q[state][action] = self.q[state][action] + (self.alpha * (target - self.q[state][action]))

    def get_reward(self):
        if self.has_touched_finish() == 1:
            return 100000  # Positive reward for reaching the finish line
        elif self.has_touched_finish() == -1:
            return -100000  # Negative reward for colliding with the finish line from the wrong side
        elif self.is_collision():
            return -100  # Negative reward for collisions
        elif not self.alive:
            return -100  # Negative reward for going out of bounds or other failure conditions
        else:
            return self.distance / (Car.CAR_SIZE_X / 2)

    def coord_to_state(self, track):
        return int(self.position[1]) * track.width + int(self.position[0])


def run_simulation(map_path='tracks/track01.png', is_training=True):
    my_track = Track(map_path)
    pg.init()
    flags = pg.SCALED | pg.FULLSCREEN
    screen = pg.display.set_mode((my_track.map_width, my_track.map_height), flags)
    my_track.load_game_map()
    # clock = pg.time.Clock()

    ### ###

    q_table = defaultdict(lambda: np.zeros(5))

    episodes = 10000
    epsilon = 1.0  # Allow the model to do a lot of trial and error on the beggining
    epsilon_decay = 0.00013  # Decay per episode.

    lr = 1.0  # Initial Learning Rate
    lr_decay = 0.001
    rewards = np.zeros(episodes)

    start_pos_x, start_pos_y, angle = my_track.start_pos
    speed = 10
    start_pos_y -= CarAgent.CAR_SIZE_Y // 2
    top_start_line, bottom_start_line = my_track.get_start_line_points()

    start_time = time.time()
    finish = []

    for i in range(episodes):

        if i % 1000 == 0:
            print(i)

        car = CarAgent('cars/car2d.png', start_pos_x, start_pos_y, angle, speed, my_track.game_map,
                       my_track.border_color, my_track.width, my_track.height, top_start_line, bottom_start_line)
        car.q = q_table
        car.update()

        while car.alive:

            epsilon = max(epsilon - epsilon_decay, 0.01)
            lr = max(lr - lr_decay, 0.01)
            car.alpha = lr

            screen.blit(my_track.game_map, (0, 0))
            car.draw(screen)

            if car.has_touched_finish() == 1:
                finish.append(i)
                print(f"Touched finish at ep: {i}")

            # state = car.coord_to_state(my_track)
            state = (int(car.position[0]), int(car.position[1]))

            action = car.select_action(state, epsilon)

            car.move(action)
            car.update()

            # new_state = car.coord_to_state(my_track)
            new_state = (int(car.position[0]), int(car.position[1]))

            car.check_engine()
            if state == new_state:
                car.alive = False

            reward = car.get_reward()

            car.updateExperience(state, action, reward, new_state)

            pg.display.flip()
            # clock.tick(60)

        rewards[i] = reward

    print(finish)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f'Time elapsed: {elapsed_time} seconds')

    if is_training:
        plt.plot(rewards)
        plt.savefig('alg_qlearning_track01.png')

        f = open("alg_qlearning_track01.pkl", "wb")
        pickle.dump(q_table, f)
        f.close()

    print(np.max(rewards))


run_simulation()