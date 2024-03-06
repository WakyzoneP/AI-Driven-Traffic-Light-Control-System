import random
import pygame

from colors import RED
from constants import CAR_SPEED, CAR_WIDTH, CAR_HEIGHT, LINE_WIDTH, ROAD_WIDTH, Location, Orientation
from objects.intersection import Intersection


class Car:
    def __init__(self, init_location, final_location, intersection):
        self.color = RED
        self.init_location = init_location
        self.final_location = final_location
        self.intersection: Intersection = intersection
        if self.init_location == Location.UP or self.init_location == Location.DOWN:
            self.orientation = Orientation.VERTICAL
        if self.init_location == Location.RIGHT or self.init_location == Location.LEFT:
            self.orientation = Orientation.HORIZONTAL
        self._position()
            
    def _position(self):
        if self.init_location == Location.UP:
            self.x = self.intersection.x + (self.intersection.width - ROAD_WIDTH // 2 - LINE_WIDTH // 2 - CAR_WIDTH // 2) // 2
            self.y = self.intersection.y
        if self.init_location == Location.RIGHT:
            self.x = self.intersection.x + self.intersection.width - CAR_WIDTH
            self.y = self.intersection.y + (self.intersection.height - ROAD_WIDTH // 2 - LINE_WIDTH // 2 - CAR_WIDTH // 2) // 2
        if self.init_location == Location.DOWN:
            self.x = self.intersection.x + (self.intersection.width + ROAD_WIDTH // 2 + LINE_WIDTH // 2 - CAR_WIDTH // 2) // 2
            self.y = self.intersection.y + self.intersection.height - CAR_WIDTH
        if self.init_location == Location.LEFT:
            self.x = self.intersection.x
            self.y = self.intersection.y + (self.intersection.height + ROAD_WIDTH // 2 + LINE_WIDTH // 2 - CAR_WIDTH // 2) // 2
        
    def draw(self, window):
        if self.orientation == Orientation.HORIZONTAL:
            pygame.draw.rect(
                window,
                self.color,
                (self.x, self.y, CAR_WIDTH, CAR_HEIGHT),
            )
        if self.orientation == Orientation.VERTICAL:
            pygame.draw.rect(
                window,
                self.color,
                (self.x, self.y, CAR_HEIGHT, CAR_WIDTH),
            )
            
    def _choose_path(self):
        random_number = random.randint(0, 2)
        if self.init_location == Location.UP:
            if random_number == 0:
                self.final_location = Location.RIGHT
            elif random_number == 1:
                self.final_location = Location.DOWN
            elif random_number == 2:
                self.final_location = Location.LEFT
        elif self.init_location == Location.RIGHT:
            if random_number == 0:
                self.final_location = Location.DOWN
            elif random_number == 1:
                self.final_location = Location.LEFT
            elif random_number == 2:
                self.final_location = Location.UP
        elif self.init_location == Location.DOWN:
            if random_number == 0:
                self.final_location = Location.LEFT
            elif random_number == 1:
                self.final_location = Location.UP
            elif random_number == 2:
                self.final_location = Location.RIGHT
        elif self.init_location == Location.LEFT:
            if random_number == 0:
                self.final_location = Location.UP
            elif random_number == 1:
                self.final_location = Location.RIGHT
            elif random_number == 2:
                self.final_location = Location.DOWN
                
    def _move_from_up(self):
        if self.final_location == Location.RIGHT:
            if self.y < self.intersection.y + (2 * self.intersection.height + LINE_WIDTH + ROAD_WIDTH) // 4 - CAR_WIDTH:
                self.y += CAR_SPEED
                if self.y >= self.intersection.y + (2 * self.intersection.height + LINE_WIDTH + ROAD_WIDTH) // 4 - CAR_WIDTH:
                    self.y = self.intersection.y + (2 * self.intersection.height + LINE_WIDTH + ROAD_WIDTH) // 4 - CAR_WIDTH // 4
                    self.orientation = Orientation.HORIZONTAL
            elif self.x < self.intersection.x + self.intersection.width:
                self.x += CAR_SPEED
                if self.x >= self.intersection.x + self.intersection.width:
                    self.intersection = self.intersection.neighbours['right']
                    if self.intersection is not None:
                        self.init_location = Location.LEFT
                        self._choose_path()
                        self._position()
        if self.final_location == Location.DOWN:
            if self.y < self.intersection.y + self.intersection.height:
                self.y += CAR_SPEED
            elif self.y >= self.intersection.y + self.intersection.height:
                self.intersection = self.intersection.neighbours['bottom']
                if self.intersection is not None:
                    self.init_location = Location.UP
                    self._choose_path()
                    self._position()
        if self.final_location == Location.LEFT:
            if self.y < self.intersection.y + self.intersection.height // 2 - CAR_WIDTH:
                self.y += CAR_SPEED
                if self.y >= self.intersection.y + self.intersection.height // 2 - CAR_WIDTH:
                    self.x = self.intersection.x + self.intersection.width // 2 - CAR_WIDTH
                    self.orientation = Orientation.HORIZONTAL
            elif self.x > self.intersection.x - CAR_WIDTH:
                self.x -= CAR_SPEED
                if self.x <= self.intersection.x - CAR_WIDTH:
                    self.intersection = self.intersection.neighbours['left']
                    if self.intersection is not None:
                        self.init_location = Location.RIGHT
                        self._choose_path()
                        self._position()
                    
    def _move_from_right(self):
        if self.final_location == Location.DOWN:
            if self.x > self.intersection.x + (self.intersection.width - ROAD_WIDTH // 2 - LINE_WIDTH // 2 - CAR_WIDTH // 2) // 2:
                self.x -= CAR_SPEED
                if self.x <= self.intersection.x + (self.intersection.width - ROAD_WIDTH // 2 - LINE_WIDTH // 2 - CAR_WIDTH // 2) // 2:
                    self.x = self.intersection.x + (self.intersection.width - ROAD_WIDTH // 2 - LINE_WIDTH // 2 - CAR_WIDTH // 2) // 2
                    self.orientation = Orientation.VERTICAL
            elif self.y < self.intersection.y + self.intersection.height:
                self.y += CAR_SPEED
                if self.y >= self.intersection.y + self.intersection.height:
                    self.intersection = self.intersection.neighbours['bottom']
                    if self.intersection is not None:
                        self.init_location = Location.UP
                        self._choose_path()
                        self._position()
        if self.final_location == Location.LEFT:
            if self.x > self.intersection.x - CAR_WIDTH:
                self.x -= CAR_SPEED
            elif self.x <= self.intersection.x - CAR_WIDTH:
                self.intersection = self.intersection.neighbours['left']
                if self.intersection is not None:
                    self.init_location = Location.RIGHT
                    self._choose_path()
                    self._position()
        if self.final_location == Location.UP:
            if self.x > self.intersection.x + (self.intersection.width + ROAD_WIDTH // 2 + LINE_WIDTH // 2 - CAR_WIDTH // 2) // 2:
                self.x -= CAR_SPEED
                if self.x <= self.intersection.x + (self.intersection.width + ROAD_WIDTH // 2 + LINE_WIDTH // 2 - CAR_WIDTH // 2) // 2:
                    self.y = self.intersection.y + self.intersection.height // 2 - CAR_WIDTH
                    self.orientation = Orientation.VERTICAL
            elif self.y > self.intersection.y - CAR_WIDTH:
                self.y -= CAR_SPEED
                if self.y <= self.intersection.y - CAR_WIDTH:
                    self.intersection = self.intersection.neighbours['top']
                    if self.intersection is not None:
                        self.init_location = Location.DOWN
                        self._choose_path()
                        self._position()
    
    def _move_from_down(self):
        if self.final_location == Location.LEFT:
            if self.y > self.intersection.y + (self.intersection.height - ROAD_WIDTH // 2 - LINE_WIDTH // 2 - CAR_WIDTH // 2) // 2:
                self.y -= CAR_SPEED
                if self.y <= self.intersection.y + (self.intersection.height - ROAD_WIDTH // 2 - LINE_WIDTH // 2 - CAR_WIDTH // 2) // 2:
                    self.y = self.intersection.y + (self.intersection.height - ROAD_WIDTH // 2 - LINE_WIDTH // 2 - CAR_WIDTH // 2) // 2
                    self.orientation = Orientation.HORIZONTAL
            elif self.x > self.intersection.x - CAR_WIDTH:
                self.x -= CAR_SPEED
                if self.x <= self.intersection.x - CAR_WIDTH:
                    self.intersection = self.intersection.neighbours['left']
                    if self.intersection is not None:
                        self.init_location = Location.RIGHT
                        self._choose_path()
                        self._position()
        if self.final_location == Location.UP:
            if self.y > self.intersection.y - CAR_WIDTH:
                self.y -= CAR_SPEED
            elif self.y <= self.intersection.y - CAR_WIDTH:
                self.intersection = self.intersection.neighbours['top']
                if self.intersection is not None:
                    self.init_location = Location.DOWN
                    self._choose_path()
                    self._position()
        if self.final_location == Location.RIGHT:
            if self.y > self.intersection.y + (self.intersection.height - ROAD_WIDTH // 2 - LINE_WIDTH // 2 - CAR_WIDTH // 2) // 2:
                self.y -= CAR_SPEED
                if self.y <= self.intersection.y + (self.intersection.height - ROAD_WIDTH // 2 - LINE_WIDTH // 2 - CAR_WIDTH // 2) // 2:
                    self.x = self.intersection.x + self.intersection.width // 2 + CAR_WIDTH // 2
                    self.orientation = Orientation.HORIZONTAL
            elif self.x < self.intersection.x + self.intersection.width:
                self.x += CAR_SPEED
                if self.x >= self.intersection.x + self.intersection.width:
                    self.intersection = self.intersection.neighbours['right']
                    if self.intersection is not None:
                        self.init_location = Location.LEFT
                        self._choose_path()
                        self._position()
                
    def _move_from_left(self):
        if self.final_location == Location.UP:
            if self.x < self.intersection.x + (self.intersection.width + ROAD_WIDTH // 2 + LINE_WIDTH // 2 - CAR_WIDTH // 2) // 2:
                self.x += CAR_SPEED
                if self.x >= self.intersection.x + (self.intersection.width + ROAD_WIDTH // 2 + LINE_WIDTH // 2 - CAR_WIDTH // 2) // 2:
                    self.x = self.intersection.x + (self.intersection.width + ROAD_WIDTH // 2 + LINE_WIDTH // 2 - CAR_WIDTH // 2) // 2
                    self.orientation = Orientation.VERTICAL
            elif self.y > self.intersection.y - CAR_WIDTH:
                self.y -= CAR_SPEED
                if self.y <= self.intersection.y - CAR_WIDTH:
                    self.intersection = self.intersection.neighbours['top']
                    if self.intersection is not None:
                        self.init_location = Location.DOWN
                        self._choose_path()
                        self._position()
        if self.final_location == Location.RIGHT:
            if self.x < self.intersection.x + self.intersection.width:
                self.x += CAR_SPEED
            elif self.x >= self.intersection.x + self.intersection.width:
                self.intersection = self.intersection.neighbours['right']
                if self.intersection is not None:
                    self.init_location = Location.LEFT
                    self._choose_path()
                    self._position()
        if self.final_location == Location.DOWN:
            if self.x < self.intersection.x + (self.intersection.width - ROAD_WIDTH // 2 - LINE_WIDTH // 2 - CAR_WIDTH // 2) // 2:
                self.x += CAR_SPEED
                if self.x >= self.intersection.x + (self.intersection.width - ROAD_WIDTH // 2 - LINE_WIDTH // 2 - CAR_WIDTH // 2) // 2:
                    self.x = self.intersection.x + (self.intersection.width - ROAD_WIDTH // 2 - LINE_WIDTH // 2 - CAR_WIDTH // 2) // 2
                    self.orientation = Orientation.VERTICAL
            elif self.y < self.intersection.y + self.intersection.height:
                self.y += CAR_SPEED
                if self.y >= self.intersection.y + self.intersection.height:
                    self.intersection = self.intersection.neighbours['bottom']
                    if self.intersection is not None:
                        self.init_location = Location.UP
                        self._choose_path()
                        self._position()
    
    def move(self):
        if self.init_location == Location.UP:
            self._move_from_up()
        elif self.init_location == Location.RIGHT:
            self._move_from_right()
        elif self.init_location == Location.DOWN:
            self._move_from_down()
        elif self.init_location == Location.LEFT:
            self._move_from_left()