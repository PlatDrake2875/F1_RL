import pygame as pg
import math


class Car:
    START_SPEED = 20
    BORDER_EDGE = 20
    CAR_SIZE_X = 60
    CAR_SIZE_Y = 60
    
    def __init__(self, car_sprite, pos_x, pos_y, angle, speed, game_map, border_color, map_width, map_height):
        self.sprite = pg.image.load(car_sprite).convert()
        self.sprite = pg.transform.scale(self.sprite, (Car.CAR_SIZE_X, Car.CAR_SIZE_Y))
        
        self.map_width = map_width
        self.map_height = map_height
        
        self.position = [pos_x, pos_y]
        self.angle = angle
        self.speed = speed
        
        self.center = [self.position[0] + Car.CAR_SIZE_X / 2, self.position[1] + Car.CAR_SIZE_Y / 2]
        
        self.alive = True
        
        self.distance = 0
        self.time = 0
        
        self.corners = []
        
        self.game_map = game_map
        self.border_color = border_color
        
    def draw(self, screen):
        screen.blit(pg.transform.rotate(self.sprite, self.angle), self.position)
        
    def is_out_of_bounds(self, x , y):
        return x < 0 or x >= self.map_width or y < 0 or y >= self.map_height
        
    def is_collision(self, point):
        return self.game_map.get_at((int(point[0]), int(point[1]))) == self.border_color
        
    def check_collision(self):
        self.alive = True
        
        for corner in self.corners:
            if self.is_collision(corner):
                self.alive = False
                break
        
    def rotate_center(self, image, angle):
        orig_rect = image.get_rect()
        rot_image = pg.transform.rotate(image, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        
        return rot_image
    
    def update(self):                 
        self.rotated_sprite = self.rotate_center(self.sprite, self.angle)
        # self.position[0] += self.speed * pg.math.Vector2(pg.math.Vector2(1, 0).rotate(self.angle)).x
        self.position[0] += self.speed * math.cos(math.radians(360 - self.angle))
        self.position[0] = min(max(Car.BORDER_EDGE, self.position[0]), self.map_width - Car.CAR_SIZE_X - Car.BORDER_EDGE)
        
        self.distance += self.speed
        self.time += 1
        
        # self.position[1] += self.speed * pg.math.Vector2(pg.math.Vector2(1, 0).rotate(self.angle)).y
        self.position[1] += self.speed * math.sin(math.radians(360 - self.angle))
        self.position[1] = min(max(Car.BORDER_EDGE, self.position[1]), self.map_height - Car.CAR_SIZE_Y - Car.BORDER_EDGE)
        
        self.center = [self.position[0] + Car.CAR_SIZE_X / 2, self.position[1] + Car.CAR_SIZE_Y / 2]
        
        length = Car.CAR_SIZE_X / 2
        # self.corners = [[self.center[0] + length * pg.math.Vector2(pg.math.Vector2(1, 0).rotate(self.angle)).x, self.center[1] + length * pg.math.Vector2(pg.math.Vector2(1, 0).rotate(self.angle)).y],
        #                 [self.center[0] - length * pg.math.Vector2(pg.math.Vector2(1, 0).rotate(self.angle)).x, self.center[1] - length * pg.math.Vector2(pg.math.Vector2(1, 0).rotate(self.angle)).y],
        #                 [self.center[0] - length * pg.math.Vector2(pg.math.Vector2(1, 0).rotate(self.angle + 90)).x, self.center[1] - length * pg.math.Vector2(pg.math.Vector2(1, 0).rotate(self.angle + 90)).y],
        #                 [self.center[0] + length * pg.math.Vector2(pg.math.Vector2(1, 0).rotate(self.angle + 90)).x, self.center[1] + length * pg.math.Vector2(pg.math.Vector2(1, 0).rotate(self.angle + 90)).y]]
        
        self.corners = [[self.center[0] + length * math.cos(math.radians(360 - self.angle)), self.center[1] + length * math.sin(math.radians(360 - self.angle))],
                        [self.center[0] - length * math.cos(math.radians(360 - self.angle)), self.center[1] - length * math.sin(math.radians(360 - self.angle))],
                        [self.center[0] - length * math.cos(math.radians(360 - self.angle + 90)), self.center[1] - length * math.sin(math.radians(360 - self.angle + 90))],
                        [self.center[0] + length * math.cos(math.radians(360 - self.angle + 90)), self.center[1] + length * math.sin(math.radians(360 - self.angle + 90))]]
        
        
        self.check_collision()
        self.check_engine()
     
    def check_engine(self):
        if self.speed <= 0:
            self.speed = 0
            self.alive = False
            
    def get_data(self):
        result = [0, 0, 0, 0, 0]
        
        for i, sensor in enumerate(self.sensors):
            result[i] = int(sensor[1] / 30)
            
        return result
    
    def is_alive(self):
        return self.alive
    
    