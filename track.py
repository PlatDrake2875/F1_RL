import pygame as pg
import math


class Track:
    """Represents a track in a 2D racing game.

    This class is responsible for loading the game track, identifying starting
    positions based on specific criteria, and determining if a point is out of bounds.

    Attributes:
        start_pos (tuple): The starting position on the track, including the angle (x, y, angle).
        width (int): The width of the track.
        height (int): The height of the track.
        game_map (Surface): A Pygame Surface object representing the game track.
        border_color (tuple): The RGBA color of the track's border.
        map_width (int): The width of the map area.
        map_height (int): The height of the map area.
    """

    def __init__(self, track_file, border_color=(255, 255, 255, 255), map_width=1920, map_height=1080):
        """Initializes the Track with the given parameters.

        Args:
            track_file (str): The filepath to the track image.
            border_color (tuple): The color of the border of the track (default is white).
            map_width (int): The width of the game map.
            map_height (int): The height of the game map.
        """
        self.start_pos = None
        self.width = None
        self.height = None
        self.game_map = track_file
        self.border_color = border_color
        self.map_width = map_width
        self.map_height = map_height

    def load_game_map(self):
        """Loads the game map from the track file and sets the starting position."""
        self.game_map = pg.image.load(self.game_map).convert()
        self.width = self.game_map.get_width()
        self.height = self.game_map.get_height()
        self.set_starting_position()

    def find_pixel(self, start, end, step, condition):
        """Finds a pixel that meets a given condition.

        Args:
            start (int): The starting index to begin the search.
            end (int): The ending index to stop the search.
            step (int): The step size for the search.
            condition (function): A function that returns True if the pixel meets the desired condition.

        Returns:
            tuple: The coordinates of the found pixel, or None if no pixel meets the condition.
        """
        for x in range(start, end, step):
            for y in range(self.height):
                if condition(self.game_map.get_at((x, y))):
                    return x, y
        return None

    def set_starting_position(self):
        """Determines the starting position on the track based on specific criteria.

        The starting position is identified by finding specific pixels on the track and
        calculating the midpoint and angle between them.

        Returns:
            tuple: The x and y coordinates and angle of the starting position.
        """
        bottom_left_green = self.find_pixel(0, self.width, 1, lambda color: color == (0, 255, 0, 255))
        top_left_green = self.find_pixel(self.width - 1, -1, -1, lambda color: color == (0, 255, 0, 255))

        if bottom_left_green and top_left_green:
            angle = math.atan2(top_left_green[0] - bottom_left_green[0],
                               top_left_green[1] - bottom_left_green[1]) * 180 / math.pi
            midpoint = ((top_left_green[0] + bottom_left_green[0]) // 2,
                        (top_left_green[1] + bottom_left_green[1]) // 2)
            self.start_pos = (midpoint[0], midpoint[1], angle)
            return midpoint[0], midpoint[1], angle
        else:
            self.start_pos = (0, 0, 0)
            return 0, 0, 0

    def out_of_bounds(self, x, y):
        """Checks if the given coordinates are out of the bounds of the track.

        Args:
            x (int): The x-coordinate to check.
            y (int): The y-coordinate to check.

        Returns:
            bool: True if the coordinates are out of bounds, False otherwise.
        """
        return x < 0 or x >= self.width or y < 0 or y >= self.height
