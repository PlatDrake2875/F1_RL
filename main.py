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

class TestCar(Car):

    def get_reward(self):
        a = 0
        if self.is_collision():
            a = -10
        if not self.alive:
            a -= 10
        # if self.has_touched_finish() == -1:
        #     self.alive = False
        #     return -10000
        # return self.distance + self.has_touched_finish() * 100000
        return self.distance / (Car.CAR_SIZE_X / 2) + self.has_touched_finish() * 100000 + a

def state_to_coord(track, state):
    return (state % track.width, state // track.width)

def coord_to_state(track, x, y):
    return y * track.width + x

def run_simulation(map_path='tracks/track01_resized.png', speed = 10, is_training = True):  

    my_track = Track(map_path)

    pg.init()

    flags = pg.SCALED | pg.FULLSCREEN
    screen = pg.display.set_mode((my_track.map_width, my_track.map_height), flags)

    my_track.load_game_map()
    # clock = pg.time.Clock()
    
    
    ### ###

    episodes = 10000
    epsilon = 1.0 # Allow the model to do a lot of trial and error on the beggining
    epsilon_decay = 0.00015 # Decay per episode.

    lr = 1.0 #Initial Learning Rate
    lr_decay = epsilon_decay
    min_lr = 0.001 #Minimum Learning Rate

    gamma = 1.0

    states = my_track.width * my_track.height # x=width, y=height
    
    if(is_training):
        q = np.random.uniform(-1, 1, (states, 8))
        # q = np.zeros((states, 8))
    else:
        f = open('alg_qlearning_track01.pkl', 'rb')
        q = pickle.load(f)
        f.close()

    rewards = np.zeros(episodes)

    # rewards_per_episode = np.zeros(episodes)

    finish = False

    for i in range(episodes):

        if i % 100 == 0:
            print(i)


        start_pos_x, start_pos_y, angle = my_track.start_pos
        start_pos_y -= TestCar.CAR_SIZE_Y // 2
        top_start_line, bottom_start_line = my_track.get_start_line_points()

        car = TestCar('cars/car2d.png', start_pos_x, start_pos_y, angle, speed, my_track.game_map, my_track.border_color, my_track.width, my_track.height, top_start_line, bottom_start_line)
        
        car.update()

        max_reward = -1
        
        while True:

            if car.has_touched_finish() == 1:
                # finish = True
                # break
                print(f"Touched finish at ep: {i}")

            for event in pg.event.get():
                if event.type == QUIT:
                    pg.quit()
                    sys.exit()
                    
            
            screen.blit(my_track.game_map, (0, 0))

            if car.speed == 0:
                car.alive = False
            if car.is_alive():
                car.draw(screen)
            else:
                break

            if np.random.uniform(0, 1) < epsilon:
                action = random.randint(0, 7)
            else:
                action = np.argmax(q[state, :])

            
            state = coord_to_state(my_track, int(car.position[0]), int(car.position[1]))
            
            car.move(action)
            car.update()

            new_state = coord_to_state(my_track, int(car.position[0]), int(car.position[1]))

            if state == new_state:
                # reward = -100
                car.alive = False

            reward = car.get_reward()

            # q[state,action] = q[state,action] + lr * (
            #             reward + gamma * np.max(q[new_state, :]) - q[state,action]
            # )

            q[state,action] = (1 - lr) * q[state,action] + lr * (
                        reward + gamma * np.max(q[new_state, :]))

            epsilon = max(epsilon - epsilon_decay, 0.01)
            lr = max(lr - lr_decay, min_lr)

            if reward > max_reward:
                max_reward = reward

            pg.display.flip()
            # clock.tick(60)
        
        rewards[i] = max_reward

        # if finish:
        #     print(f"Reached finish at episode {i}")
        #     break

        # while True:
        #     pg.display.flip()
        #     clock.tick(60)
        #     car.draw(screen)
        #     for event in pg.event.get():
        #         if event.type == QUIT:
        #             pg.quit()
        #             sys.exit()

    # sum_rewards = np.zeros(episodes)
    # for t in range(episodes):
    #     sum_rewards[t] = np.sum(rewards[max(0, t-100):(t+1)])
    plt.plot(rewards)
    plt.savefig('alg_qlearning_track01.png')

    if is_training:
        f = open("alg_qlearning_track01.pkl","wb")
        pickle.dump(q, f)
        f.close()

    print(np.max(rewards))
                
run_simulation()