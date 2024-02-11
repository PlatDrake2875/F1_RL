import pygame as pg
import math

class Track:
    def __init__ (self, track_file, border_color=(255, 255, 255, 255), map_width=1920, map_height=1080):
        self.game_map = track_file
        
        self.border_color = border_color
        self.map_width = map_width
        self.map_height = map_height
        
    def load_game_map(self):
        self.game_map = pg.image.load(self.game_map).convert()
        
        self.width = self.game_map.get_width()
        self.height = self.game_map.get_height()
        
        self.set_starting_position()
        
    def set_starting_position(self):
        # Identify the bottom-left most green pixel
        blg = ()
        for x in range(self.width):
            for y in range(self.height):
                if self.game_map.get_at((x, y)) == (0, 255, 0, 255):
                    blg = (x, y)
                    break
            if blg:
                break
        
        # Identify the top-left most green pixel
        tlg = ()
        for y in range(self.height -1 , -1, -1):
            for x in range(self.width):
                if self.game_map.get_at((x, y)) == (0, 255, 0, 255):
                    tlg = (x, y)
                    break
            if tlg:
                break
            
        # Find the angle of the line between the two points and oX in degrees
        angle = math.atan2(tlg[0] - blg[0], tlg[1] - blg[1]) * 180 / math.pi
        
        # Find the midpoint of the line
        midpoint = ((tlg[0] + blg[0]) // 2, (tlg[1] + blg[1]) // 2)
        
        self.start_pos = (midpoint[0], midpoint[1], angle)
        
        return (midpoint[0], midpoint[1], angle)
    
    def out_of_bounds(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return True
        return False
    