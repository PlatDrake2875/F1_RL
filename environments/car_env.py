import os
import random

import numpy as np
import pygame

import gymnasium as gym
from gymnasium import spaces

import cv2
import numpy as np
from gymnasium.spaces import Dict, Box


class TrackUtils:
    @staticmethod
    def get_start_rect_coords(image_path, debug=False):
        # Load the image
        image = cv2.imread(image_path)

        # Define the range for green color
        lower_green = np.array([0, 255, 0])
        upper_green = np.array([0, 255, 0])

        # Create a mask for green color
        green_mask = cv2.inRange(image, lower_green, upper_green)

        # Find contours in the green mask
        contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        largest_area = 0
        largest_rectangle = None

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            if area > largest_area:
                largest_area = area
                largest_rectangle = (x, y, w, h)

        if largest_rectangle is not None:
            x, y, w, h = largest_rectangle
            # Draw the largest rectangle on the image
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
            # Show the image
            if debug:
                print(f"Largest green rectangle found at: {(x, y, w, h)} with area: {largest_area}")
                cv2.imshow('Image with largest green rectangle', image)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
        else:
            print("No green rectangles found.")

        return largest_rectangle

    @staticmethod
    def resize_and_save_if_needed(image_path, new_width, new_height, save_path):
        # First, try to load the image from the save_path
        if os.path.exists(save_path):
            image = cv2.imread(save_path)
            if image is not None and image.shape[1] == new_width and image.shape[0] == new_height:
                print(f"Using existing resized image from: {save_path}")
                return image
            else:
                print(f"Found image at {save_path} does not match the desired size. Resizing and saving.")

        # If the image doesn't exist or doesn't match the desired size, load the original and resize
        image = cv2.imread(image_path)
        if image is None:
            print(f"Original image file not found: {image_path}")
            return None

        resized_image = cv2.resize(image, (new_width, new_height))
        cv2.imwrite(save_path, resized_image)
        print(f"Resized image saved to: {save_path}")
        return resized_image

    @staticmethod
    def get_image(path):
        image_path = path
        image = None
        if not os.path.exists(image_path):
            print(f"Image file not found: {image_path}")
        else:
            image = cv2.imread(image_path)
        return image

    @staticmethod
    def get_image_size(path):
        image = TrackUtils.get_image(path)
        # TrackUtils.display_image(path)
        return image.shape[0], image.shape[1]

    @staticmethod
    def display_image(path):
        image = TrackUtils.get_image(path)
        cv2.imshow('Image', image)
        cv2.waitKey(0)


class Car:
    CAR_WIDTH = 30
    CAR_HEIGHT = 30

    def __init__(self, car_path, speed=5, angle=5):
        self.angle = angle
        self.speed = speed
        # Directly use the resized image path after ensuring it's created
        self.car_path = f"car2d_{Car.CAR_WIDTH}_{Car.CAR_HEIGHT}.png"
        # Ensure the resized image is created if needed
        TrackUtils.resize_and_save_if_needed(car_path, Car.CAR_WIDTH, Car.CAR_HEIGHT, self.car_path)
        # Update car_size with the actual dimensions
        self.car_size = (Car.CAR_WIDTH, Car.CAR_HEIGHT)

    def apply_action(self, action):
        if action == 0:
            return
        elif action == 1:
            self.add_speed(5)
        elif action == 2:
            self.add_speed(-5)
        elif action == 3:
            self.add_angle(2)
        elif action == 4:
            self.add_angle(-2)

    def add_speed(self, speed):
        self.speed += speed

    def add_angle(self, angle):
        self.angle += angle

    def calculate_movement(self):
        # Convert angle from degrees to radians for calculation
        angle_rad = np.radians(self.angle)

        # Calculate the change in position
        dx = self.speed * np.cos(angle_rad)
        dy = -self.speed * np.sin(angle_rad)  # Negative because screen y-coordinates increase downwards

        return dx, dy


class Track:
    TRACK_WIDTH = 1920
    TRACK_HEIGHT = 1080

    def __init__(self, track_path):
        self.track_path = track_path
        resized_track_image_path = f"track01_{Track.TRACK_WIDTH}_{Track.TRACK_HEIGHT}.png"
        resized_track_image = TrackUtils.resize_and_save_if_needed(track_path, Track.TRACK_WIDTH, Track.TRACK_HEIGHT,
                                                                   resized_track_image_path)
        if resized_track_image is not None:
            self.track_image = cv2.cvtColor(resized_track_image, cv2.COLOR_BGR2GRAY)
            self.track_size = (Track.TRACK_WIDTH, Track.TRACK_HEIGHT)
        else:
            print(f"Track file not found: {track_path}")
            self.track_image = None
            self.track_size = (0, 0)

    def calculate_distances_to_edges(self, _agent_location, car_size):
        # Get the car's center position
        center_x, center_y = _agent_location + car_size[0] // 2

        # Helper function to find distance to the nearest white pixel in a given direction
        def find_distance_to_edge(start_x, start_y, delta_x, delta_y):
            distance = 0
            x, y = start_x, start_y
            while 0 <= x < self.track_image.shape[1] and 0 <= y < self.track_image.shape[0]:
                if self.track_image[y, x] == 255:  # White pixel found
                    return distance
                x += delta_x
                y += delta_y
                distance += 1
            return np.inf

        # Calculate distances in all four directions
        distances = np.array([
            find_distance_to_edge(center_x, center_y, -1, 0),  # Left
            find_distance_to_edge(center_x, center_y, 1, 0),  # Right
            find_distance_to_edge(center_x, center_y, 0, -1),  # Up
            find_distance_to_edge(center_x, center_y, 0, 1)  # Down
        ], dtype=np.float32)

        return distances

    def check_collision(self, _agent_location, car_size):
        # Calculate the car's bounding box based on its current position and size
        x1 = int(_agent_location[0])
        y1 = int(_agent_location[1])
        x2 = int(x1 + car_size[0])
        y2 = int(y1 + car_size[1])

        # Ensure the bounding box is within the track boundaries to avoid indexing errors
        x1, x2 = max(0, x1), min(self.track_image.shape[1], x2)
        y1, y2 = max(0, y1), min(self.track_image.shape[0], y2)

        # Extract the area of the track image where the car is located
        car_area = self.track_image[y1:y2, x1:x2]

        # Check if there are any white pixels in this area
        collision = np.any(car_area == 255)

        return collision


class F1_Env(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}

    def __init__(self, track_path="./tracks/track01.png", car_path="./cars/car2d.png", render_mode=None):

        self._agent_location = None
        self.car = Car(car_path)
        self.track = Track(track_path)

        self.window_track_size = (Track.TRACK_WIDTH, Track.TRACK_HEIGHT)  # Update this line
        self.start_rect_coords = TrackUtils.get_start_rect_coords(track_path)

        self.observation_space = Dict({
            "position": Box(low=np.array([0, 0]), high=np.array(self.track.track_size), dtype=np.float32),
            "angle": Box(low=np.array([-360]), high=np.array([360]), dtype=np.float32),
            "speed": Box(low=np.array([0]), high=np.array([np.inf]), dtype=np.float32),
            "distances_to_edges": Box(low=np.array([0, 0, 0]), high=np.array([np.inf, np.inf, np.inf]),
                                      dtype=np.float32),
        })

        self.action_space = spaces.Discrete(5)  # Reflect correct number of actions

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode
        self.window = None
        if self.render_mode == "human":
            self._init_render()

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self.car.speed = 0
        self.car.angle = 0  # Starting angle pointing to the right

        # Seed the random number generator for reproducibility
        rng = np.random.default_rng(seed)

        # Validate presence of start_rect_coords and car_size
        assert self.start_rect_coords is not None, "Starting rectangle coordinates are not defined."
        rect_x, rect_y, rect_w, rect_h = self.start_rect_coords
        car_w, car_h = self.car.car_size

        # Ensure there's enough space for the car to start
        if rect_w <= car_w or rect_h <= car_h:
            raise ValueError("The starting rectangle is too small for the car.")

        # Calculate the maximum valid starting positions for the car
        max_start_x = rect_x + rect_w - car_w
        max_start_y = rect_y + rect_h - car_h

        # Generate valid random starting position for the car
        start_x = rng.integers(rect_x, max_start_x + 1)  # +1 because the high value is exclusive
        start_y = rng.integers(rect_y, max_start_y + 1)

        self._agent_location = np.array([start_x, start_y], dtype=np.int64)

        # Return the initial observation
        return self._get_obs()

    def step(self, action):
        self.car.apply_action(action)
        self._agent_location = self.move_agent()

        terminated = self.check_collision()

        reward = -1 if terminated else 1
        observation = self._get_obs()
        info = {}

        return observation, reward, terminated, False, info

    def move_agent(self):
        # Use the calculate_movement method from the Car class
        dx, dy = self.car.calculate_movement()

        # Update the agent's position, ensuring it does not go out of bounds
        new_x = np.clip(self._agent_location[0] + dx, 0, self.track.track_size[0] - 1)
        new_y = np.clip(self._agent_location[1] + dy, 0, self.track.track_size[1] - 1)

        self._agent_location = np.array([new_x, new_y], dtype=np.int64)
        return self._agent_location

    def check_collision(self):
        return self.track.check_collision(self._agent_location, self.car.car_size)

    def _get_obs(self):
        distances_to_edges = self.track.calculate_distances_to_edges(self._agent_location, self.car.car_size)

        observation = {
            "position": self._agent_location.astype(np.float32),
            "angle": np.array([self.car.angle], dtype=np.float32),
            "speed": np.array([self.car.speed], dtype=np.float32),
            "distances_to_edges": distances_to_edges,
        }

        return observation

    def _init_render(self):
        """Initialize the rendering components."""
        print("============================================================")
        print("Initializing rendering components...")
        pygame.init()

        # Initialize the game window with the track's size
        self.window = pygame.display.set_mode(self.window_track_size)
        pygame.display.set_caption("F1 Racing Game")
        print(f"Window initialized with size: {self.window_track_size}")

        # Load and scale the track image
        try:
            track_image_path = f"track01_{Track.TRACK_WIDTH}_{Track.TRACK_HEIGHT}.png"  # Ensure using the resized path
            self.track_image_pygame = pygame.image.load(track_image_path).convert()
            print(f"Loaded track image from {track_image_path}")
        except Exception as e:
            print(f"Failed to load track image: {e}")
            return

        # Load the car image
        try:
            # Ensure using the resized image path for the car
            self.car_image_pygame = pygame.image.load(self.car.car_path).convert_alpha()
            print(f"Loaded car image from {self.car.car_path}")
        except Exception as e:
            print(f"Failed to load car image: {e}")
            return

    def render(self):
        if self.render_mode != "human":
            return
        else:
            self._render_frame()

    def _render_frame(self):
        print("============================================================")
        print("Rendering frame...")

        # Check if window is initialized
        if not self.window:
            print("Warning: Render window is not initialized.")
            return

        # Fill background
        self.window.blit(self.track_image_pygame, (0, 0))
        print(f"Background blitted at (0, 0).")

        # Calculate car's position and angle
        car_pos = (self._agent_location[0], self._agent_location[1])
        print(f"Car position: {car_pos}, Car angle: {self.car.angle}")

        try:
            car_rotated = pygame.transform.rotate(self.car_image_pygame,
                                                  -self.car.angle)  # Negative for correct rotation direction
            car_rect = car_rotated.get_rect(center=car_pos)
        except Exception as e:
            print(f"Error rotating or positioning car image: {e}")
            return

        # Draw car
        self.window.blit(car_rotated, car_rect.topleft)
        print(f"Car blitted at {car_rect.topleft}.")

        pygame.display.flip()
        print("Display flipped.")

        # Event loop to keep the window responsive
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                print("Window closed.")
