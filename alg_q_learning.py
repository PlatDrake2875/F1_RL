from car2 import Car2
from track import Track
import pygame as pg
from pygame.locals import *
import numpy as np
import math
import time
from collections import defaultdict
import matplotlib.pyplot as plt
import pickle


class CarAgent(Car2):

    MAX_LENGTH = 200

    epsilon = 1.0 # Allow the model to do a lot of trial and error on the beggining
    epsilon_decay = 0.00013 # Decay per episode.
    lr = 1.0 #Initial Learning Rate
    lr_decay = 0.00013
    gamma = 0.8

    def __init__(self, car_sprite, pos_x, pos_y, angle, speed, game_map, border_color,
                 map_width, map_height, top_start_point, bottom_start_point):
        super().__init__(car_sprite, pos_x, pos_y, angle, speed, game_map, border_color,
                 map_width, map_height, top_start_point, bottom_start_point)

        self.n_action = 5
        self.radars = []

        # action values
        self.q = defaultdict(lambda: np.zeros(self.n_action))  # action value

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

            target = reward + CarAgent.gamma * best_actionValue_fromNextState
            self.q[state][action] = self.q[state][action] + (CarAgent.lr * (target - self.q[state][action]))
            # q[state,action] = q[state,action] + lr * (
            #             reward + gamma * np.max(q[new_state, :]) - q[state,action])
            
    def get_reward(self):
        x, y = self.radars[0][-1], self.radars[1][-1]
        diff = abs(x - y)
        if self.has_touched_finish() == -1:
            return -10000
        if self.has_touched_finish() == 1:
            return 10000
        if self.speed == 0:
            return -10-diff
        if self.is_collision():
            return -10-diff
        return self.distance-diff
        
    def check_radar(self, degree):
        length = 0
        x = int(self.center[0] + length * math.cos(math.radians(360 - (self.angle + degree))))
        y = int(self.center[1] + length * math.sin(math.radians(360 - (self.angle + degree))))
        
        while not self.is_collision_points(x, y) and length < CarAgent.MAX_LENGTH:
            length += 1
            x = int(self.center[0] + length * math.cos(math.radians(360 - (self.angle + degree))))
            y = int(self.center[1] + length * math.sin(math.radians(360 - (self.angle + degree))))

        dist = int(pg.math.Vector2(x, y).distance_to(self.center))
        self.radars.append([(x, y), dist])
        
        if degree == 0:
            length = 0
            x = int(self.center[0] + length * math.cos(math.radians(360 - (self.angle + degree))))
            y = int(self.center[1] + length * math.sin(math.radians(360 - (self.angle + degree))))
            
            while not self.is_collision_points(x, y) and length < CarAgent.MAX_LENGTH + 100:
                length += 1
                x = int(self.center[0] + length * math.cos(math.radians(360 - (self.angle + degree))))
                y = int(self.center[1] + length * math.sin(math.radians(360 - (self.angle + degree))))
            
            dist = int(pg.math.Vector2(x, y).distance_to(self.center))
            self.radars.append([(x, y), dist])

    def draw(self, screen):
        super().draw(screen)        
        for r in self.radars:
            pg.draw.line(screen, (0, 255, 0), self.center, r[0], 1)
            pg.draw.circle(screen, (0, 255, 0), r[0], 5)

    def update(self):
        super().update()        
        self.radars.clear()
        self.check_radar(-90)
        self.check_radar(90)

        
def run_simulation(map_path='tracks/track01_resized.png', is_training = True):  

    my_track = Track(map_path)
    pg.init()
    flags = pg.RESIZABLE
    screen = pg.display.set_mode((my_track.map_width, my_track.map_height), flags)
    my_track.load_game_map()
    # clock = pg.time.Clock()

    q_table = defaultdict(lambda: np.zeros(5))

    episodes = 2000

    rewards = np.zeros(episodes)

    start_pos_x, start_pos_y, angle = my_track.start_pos
    speed = 5
    start_pos_y -= CarAgent.CAR_SIZE_Y // 2
    top_start_line, bottom_start_line = my_track.get_start_line_points()

    start_time = time.time()
    finish = []

    for i in range(episodes):

        if i % 500 == 0:
            print(i)
        
        car = CarAgent('cars/car2d.png', start_pos_x, start_pos_y, angle, speed, my_track.game_map, my_track.border_color, my_track.width, my_track.height, top_start_line, bottom_start_line)
        car.q = q_table
        car.update()

        max_reward = -1        
        car_start_time = time.time() 

        while car.alive:
            if time.time() - car_start_time > 30:
                break

            CarAgent.epsilon = max(CarAgent.epsilon - CarAgent.epsilon_decay, 0.01)
            CarAgent.lr = max(CarAgent.lr - CarAgent.lr_decay, 0.01)
 
            screen.blit(my_track.game_map, (0, 0))
            car.draw(screen)

            if car.has_touched_finish() == 1:
                finish.append(i)
                print(f"Touched finish at ep: {i}")

            state = (int(car.position[0]), int(car.position[1]))

            action = car.select_action(state, CarAgent.epsilon)
            dist = car.distance
            
            car.move(action)
            car.update()

            new_state = (int(car.position[0]), int(car.position[1]))

            car.check_engine()
            if state == new_state:
                car.alive = False

            reward = car.get_reward() - dist

            max_reward = max(reward, max_reward)
            car.updateExperience(state, action, reward, new_state)

            pg.display.flip()
            # clock.tick(60)
        
        rewards[i] = max_reward

    print(finish)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f'Time elapsed: {elapsed_time} seconds')

    
    if is_training:
        plt.plot(rewards)
        plt.savefig(f'alg_q_learning/alg_qlearning_{map_path[7:]}.png')

        # f = open("alg_qlearning_track01.pkl","wb")
        # pickle.dump(q_table, f)
        # f.close()

    print(np.max(rewards))
                
run_simulation()