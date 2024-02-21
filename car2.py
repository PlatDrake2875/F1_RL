import pygame as pg
import math

from track import Track


class Car2:
    """
    A Car2 class for simulating a vehicle in a 2D environment with Pygame.

    Attributes:
        START_SPEED (int): Initial speed of the car.
        BORDER_EDGE (int): Border edge distance to limit car movement.
        CAR_SIZE_X (int): Car2 sprite width in pixels.
        CAR_SIZE_Y (int): Car2 sprite height in pixels.
        Rotated_sprite (Surface): The rotated car sprite for rendering.
        Sensors (list): List of sensors attached to the car (not implemented).
        Sprite (Surface): The original car sprite loaded from an image file.
        Map_width (int): The width of the game map.
        Map_height (int): The height of the game map.
        Position (list): The car's position on the map as [x, y].
        Angle (float): The car's current angle.
        Speed (float): The car's current speed.
        Center (list): The center position of the car.
        Alive (bool): The status of the car, alive or not.
        Distance (float): The total distance traveled by the car.
        Time (int): The simulation time the car has been active.
        Corners (list): The coordinates of the car's corners.
        Game_map (Surface): The Pygame surface representing the game map.
        Border_color (Color): The color used to detect borders/collisions.
    """

    # START_SPEED = 10
    # BORDER_EDGE = 20
    # CAR_SIZE_X = 60
    # CAR_SIZE_Y = 60

    START_SPEED = 10
    BORDER_EDGE = 5
    CAR_SIZE_X = 15
    CAR_SIZE_Y = 15

    # START_SPEED = 10
    # BORDER_EDGE = 0.8
    # CAR_SIZE_X = 2.5
    # CAR_SIZE_Y = 2.5

    def __init__(self, car_sprite, pos_x, pos_y, angle, speed, game_map, border_color,
                 map_width, map_height, top_start_point, bottom_start_point):
        """
        Initializes the Car2 object with specified attributes and sprite.

        Args:
            car_sprite (str): Path to the car sprite image file.
            pos_x (float): Initial x-coordinate of the car.
            pos_y (float): Initial y-coordinate of the car.
            angle (float): Initial angle of the car.
            speed (float): Initial speed of the car.
            game_map (Surface): The game map as a Pygame surface.
            border_color (Color): The color for border collision detection.
            map_width (int): Width of the game map.
            map_height (int): Height of the game map.
        """
        self.rotated_sprite = None
        self.sensors = None
        self.sprite = pg.image.load(car_sprite).convert()
        self.sprite = pg.transform.scale(self.sprite, (Car2.CAR_SIZE_X, Car2.CAR_SIZE_Y))
        self.map_width = map_width
        self.map_height = map_height
        self.position = [pos_x, pos_y]
        self.angle = angle
        self.start_angle = angle
        self.speed = speed
        self.center = [self.position[0] + Car2.CAR_SIZE_X / 2, self.position[1] + Car2.CAR_SIZE_Y / 2]
        self.alive = True
        self.distance = 0
        self.time = 0
        self.corners = []
        self.game_map = game_map
        self.border_color = border_color
        self.angles = []
        self.speed_changes = 0
        self.top_start_point = top_start_point
        self.bottom_start_point = bottom_start_point

    def draw(self, screen):
        """
        Draws the car on the specified Pygame screen.

        Args:
            screen (Surface): The Pygame surface where the car will be drawn.
        """
        screen.blit(pg.transform.rotate(self.sprite, self.angle), self.position)

    def is_out_of_bounds(self, x, y):
        """
        Checks if the given coordinates are out of the game map boundaries.

        Args:
            x (float): The x-coordinate to check.
            y (float): The y-coordinate to check.

        Returns:
            bool: True if the coordinates are out of bounds, False otherwise.
        """
        return x < 0 or x >= self.map_width or y < 0 or y >= self.map_height

    def is_collision(self):
        """
        Determines if the car collides with the border based on the color.

        Returns:
            bool: True if the point collides with the border, False otherwise.
        """
        # Check if the corners are out of bounds
        for corner in self.corners:
            if self.is_out_of_bounds(corner[0], corner[1]):
                return True

        # Check if the line between the corners intersects with the border
        for i in range(4):
            x1, y1 = int(self.corners[i][0]), int(self.corners[i][1])
            x2, y2 = int(self.corners[(i + 1) % 4][0]), int(self.corners[(i + 1) % 4][1])

            for x in range(min(x1, x2), max(x1, x2)):
                y = int((y2 - y1) / (x2 - x1) * (x - x1) + y1)
                if self.is_collision_points(x, y):
                    return True

        return False

    def is_collision_points(self, x, y):
        """
        Determines if the given point collides with the border based on the color.

        Args:
            x, y: The (x, y) coordinates of the point to check for collision.

        Returns:
            bool: True if the point collides with the border, False otherwise.
        """
        return self.is_out_of_bounds(x, y) or self.game_map.get_at((x, y)) == self.border_color

    def check_collision(self):
        """
        Checks for collisions between the car and the border. Updates the car's
        alive status based on collision detection with the corners of the car.

        This method iterates through each corner of the car to determine if any
        corner has collided with the border, marking the car as not alive if a
        collision is detected.
        """
        self.alive = True

        if self.is_collision():
            self.alive = False
            return

    @staticmethod
    def rotate_center(image, angle):
        """
        Rotates an image around its center and returns the rotated image.

        This method creates a new rotated image such that the original image's
        center aligns with the center of the rotated image, maintaining the
        orientation of the image around its center point.

        Args:
            image (Surface): The Pygame image surface to be rotated.
            angle (float): The angle in degrees to rotate the image.

        Returns:
            Surface: A new Pygame image surface that has been rotated around its center.
        """
        original_hitbox = image.get_rect()
        rotated_image = pg.transform.rotate(image, angle)
        rotated_hitbox = original_hitbox.copy()
        rotated_hitbox.center = rotated_image.get_rect().center
        rotated_image = rotated_image.subsurface(rotated_hitbox).copy()

        return rotated_image

    def update(self):
        """
         Updates the car's state including rotation, position, collision checks, distance, and time.

         Key actions performed:
            - The sprite is rotated to match the current angle, ensuring correct orientation.
            - Position is updated based on speed and angle, with boundary checks to prevent moving outside the map.
            - Corners of the car are recalculated for accurate collision detection.
            - Collisions with map borders are checked. If found, the 'alive' status is set to False.
            - Distance traveled, and time elapsed are updated to track the car's journey.
            - Speed is checked to ensure the car remains operational. Speed dropping to zero sets 'alive' to False.
        """
        self.rotated_sprite = self.rotate_center(self.sprite, self.angle)

        self.position[0] += self.speed * math.cos(math.radians(360 - self.angle))
        self.position[0] = min(max(float(Car2.BORDER_EDGE), self.position[0]),
                               self.map_width - Car2.CAR_SIZE_X - Car2.BORDER_EDGE)

        self.position[1] += self.speed * math.sin(math.radians(360 - self.angle))
        self.position[1] = min(max(float(Car2.BORDER_EDGE), self.position[1]),
                               self.map_height - Car2.CAR_SIZE_Y - Car2.BORDER_EDGE)

        self.center = [self.position[0] + Car2.CAR_SIZE_X / 2, self.position[1] + Car2.CAR_SIZE_Y / 2]

        self.distance += self.speed
        self.time += 1

        # Update corners based on the current position and angle
        def compute_corner_cos(length_corner, angle):
            return self.center[0] + length_corner * math.cos(math.radians(360 - angle))

        def compute_corner_sin(length_corner, angle):
            return self.center[1] + length_corner * math.cos(math.radians(360 - angle))

        length = Car2.CAR_SIZE_X / 2

        self.corners = [[compute_corner_cos(length, self.angle), compute_corner_sin(length, self.angle)],
                        [compute_corner_cos(-length, self.angle), compute_corner_sin(-length, self.angle)],
                        [compute_corner_cos(length, self.angle - 90), compute_corner_sin(length, self.angle - 90)],
                        [compute_corner_cos(-length, self.angle - 90), compute_corner_sin(-length, self.angle - 90)]]

        self.check_collision()
        self.check_engine()

    def check_engine(self):
        """
        Checks the engine status of the car. If the car's speed is zero or less, the car is considered non-operational,
        and its alive status is set to False.

        This method is an additional check to ensure that the car is considered 'not alive' if it cannot move.
        """
        if self.speed <= 0:
            self.speed = 0
            self.alive = False

    def get_data(self):
        """
        Retrieves sensor data from the car. This method is intended to provide
        information from the car's sensors, such as distances to obstacles,
        which can be used for navigation and decision-making processes.

        Returns:
            list: A list of sensor data values. Each element in the list
            represents the data from one sensor, normalized or scaled as
            appropriate for the simulation's requirements. Currently, it
            returns a placeholder list with sensor data set to a scaled value
            based on a hypothetical sensor distance measurement.

        Note:
            The current implementation is a placeholder. In a complete
            implementation, this method would interact with the car's sensors
            to gather real-time data about the car's environment.
        """
        result = [0, 0, 0, 0, 0]

        for i, sensor in enumerate(self.sensors):
            result[i] = int(sensor[1] / 30)

        return result

    def is_alive(self):
        """
        Checks if the car is still operational (alive).

        This method provides a straightforward way to determine the operational
        status of the car, which is crucial for simulations where the car's
        ability to continue moving is a key factor in its success.

        Returns:
            bool: True if the car is operational (alive), False otherwise.
        """
        return self.alive

    # def move(self, move_number):
    #     if move_number == 0:
    #         self.change_angle(10) # Turn left
    #         self.change_speed(-1) # Slow down
    #     elif move_number == 1:
    #         self.change_angle(-10) # Turn right
    #         self.change_speed(-1) # Slow down
    #     elif move_number == 2:
    #         self.change_angle(20) # Turn hard  left
    #         self.change_speed(-2) # Slow down
    #     elif move_number == 3:
    #         self.change_angle(-20) # Turn hard right
    #         self.change_speed(-2) # Slow down
    #     elif move_number == 4:
    #         self.change_angle(0) # Go straight
    #         self.change_speed(-2) # Slow down
    #     elif move_number == 5:
    #         self.change_angle(0) # Go straight
    #         self.change_speed(2) # Speed up
    #     elif move_number == 6:
    #         self.change_angle(0) # Go straight
    #         self.change_speed(-4) # Hard slow down
    #     elif move_number == 7:
    #         self.change_angle(0) # Go straight
    #         self.change_speed(4) # Hard speed up
    #     else:
    #         return # Do nothing

    def move(self, move_number):
        if move_number == 1:
            self.change_speed(-1)  # Slow down
        elif move_number == 2:
            self.change_speed(1)  # Speed up
        elif move_number == 3:
            self.change_angle(45)  # Turn left
        elif move_number == 4:
            self.change_angle(-45)  # Turn right
        else:
            return 0  # Do nothing

    # def move(self, move_number):
    #     if move_number == 1:
    #         self.change_speed(-1) # Slow down
    #     elif move_number == 2:
    #         self.change_speed(1) # Speed up
    #     elif move_number == 3:
    #         self.change_angle(45) # Turn left
    #     elif move_number == 4:
    #         self.change_angle(-45) # Turn right
    #     else:
    #         return 0 # Do nothing

    def change_angle(self, angle):
        self.angle += angle
        self.angles.append(angle)

    def change_speed(self, speed):
        if self.speed + speed < 0:
            self.speed = 0
        elif self.speed + speed > 30:
            self.speed = 30
        else:
            self.speed += speed

        if speed != 0:
            self.speed_changes += 1

    def car_touches_line(self):
        # Make a rectangle around the car
        car_rect = pg.Rect(self.position[0], self.position[1], Car2.CAR_SIZE_X, Car2.CAR_SIZE_Y)

        # Check if the car rectangle intersects with the start line
        return car_rect.colliderect(pg.Rect(self.top_start_point[0], self.top_start_point[1], 10, 10)) or \
            car_rect.colliderect(pg.Rect(self.bottom_start_point[0], self.bottom_start_point[1], 10, 10))

    def is_on_left_side_of_line(self):
        if abs(abs(self.angle % 360) - abs(self.start_angle % 360)) > 45:
            # print(self.angle, self.start_angle)
            # print("Finish gresit")
            return 0
        return self.corners[0][0] < self.top_start_point[0] or self.corners[1][0] < self.top_start_point[0]

    def has_touched_finish(self):
        if self.car_touches_line():
            if self.is_on_left_side_of_line():
                return 1
            else:
                return -1

        return 0
