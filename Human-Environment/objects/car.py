import random
import pygame

from colors import RED
from constants import (
    CAR_SPEED,
    CAR_WIDTH,
    CAR_HEIGHT,
    LINE_WIDTH,
    ROAD_WIDTH,
    Location,
    Orientation,
)
from objects.intersection import Intersection


class Car:
    def __init__(self, id, init_location, final_location, intersection):
        self.id = id
        self.time_spent = 0
        self.color = RED
        self.init_location = init_location
        self.final_location = final_location
        self.intersection: Intersection = intersection
        if self.init_location == Location.UP or self.init_location == Location.DOWN:
            self.orientation = Orientation.VERTICAL
        if self.init_location == Location.RIGHT or self.init_location == Location.LEFT:
            self.orientation = Orientation.HORIZONTAL
        self._position()
        
    def _create_life(self):
        random = random.randint(0, 2)
        self.life = random * 100

    def _position(self):
        if self.orientation == Orientation.HORIZONTAL:
            self.rect = pygame.Rect(0, 0, CAR_WIDTH, CAR_HEIGHT)
        if self.orientation == Orientation.VERTICAL:
            self.rect = pygame.Rect(0, 0, CAR_HEIGHT, CAR_WIDTH)
        if self.init_location == Location.UP:
            self.rect.x = (
                self.intersection.x
                + (
                    self.intersection.width
                    - ROAD_WIDTH // 2
                    - LINE_WIDTH // 2
                    - CAR_WIDTH // 2
                )
                // 2
            )
            self.rect.y = self.intersection.y
        if self.init_location == Location.RIGHT:
            self.rect.x = self.intersection.x + self.intersection.width - CAR_WIDTH
            self.rect.y = (
                self.intersection.y
                + (
                    self.intersection.height
                    - ROAD_WIDTH // 2
                    - LINE_WIDTH // 2
                    - CAR_WIDTH // 2
                )
                // 2
            )
        if self.init_location == Location.DOWN:
            self.rect.x = (
                self.intersection.x
                + (
                    self.intersection.width
                    + ROAD_WIDTH // 2
                    + LINE_WIDTH // 2
                    - CAR_WIDTH // 2
                )
                // 2
            )
            self.rect.y = self.intersection.y + self.intersection.height - CAR_WIDTH
        if self.init_location == Location.LEFT:
            self.rect.x = self.intersection.x
            self.rect.y = (
                self.intersection.y
                + (
                    self.intersection.height
                    + ROAD_WIDTH // 2
                    + LINE_WIDTH // 2
                    - CAR_WIDTH // 2
                )
                // 2
            )

    def draw(self, window):
        if self.orientation == Orientation.HORIZONTAL:
            pygame.draw.rect(
                window,
                self.color,
                (self.rect.x, self.rect.y, CAR_WIDTH, CAR_HEIGHT),
            )
        if self.orientation == Orientation.VERTICAL:
            pygame.draw.rect(
                window,
                self.color,
                (self.rect.x, self.rect.y, CAR_HEIGHT, CAR_WIDTH),
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

    def _move_from_up(self, car_list):
        init_x = self.rect.x
        init_y = self.rect.y
        if (
            self.intersection.lights[0] == "red"
            and self.rect.y + CAR_SPEED
            > self.intersection.y
            + (self.intersection.height - ROAD_WIDTH) // 2
            - 2 * 5
            - CAR_WIDTH
            and self.rect.y + CAR_SPEED
            < self.intersection.y + (self.intersection.height - ROAD_WIDTH) // 2 - 2 * 5
        ):
            return
        if self.final_location == Location.RIGHT:
            if (
                self.rect.y
                < self.intersection.y
                + (2 * self.intersection.height + LINE_WIDTH + ROAD_WIDTH) // 4
                - CAR_WIDTH
            ):
                self.rect.y += CAR_SPEED
                if (
                    self.rect.y
                    >= self.intersection.y
                    + (2 * self.intersection.height + LINE_WIDTH + ROAD_WIDTH) // 4
                    - CAR_WIDTH
                ):
                    self.rect.y = (
                        self.intersection.y
                        + (2 * self.intersection.height + LINE_WIDTH + ROAD_WIDTH) // 4
                        - CAR_WIDTH // 4
                    )
                    self.orientation = Orientation.HORIZONTAL
            elif self.rect.x < self.intersection.x + self.intersection.width:
                self.rect.x += CAR_SPEED
                if self.rect.x >= self.intersection.x + self.intersection.width:
                    self.intersection = self.intersection.neighbours["right"]
                    if self.intersection is not None:
                        self.init_location = Location.LEFT
                        self._choose_path()
                        self._position()
        if self.final_location == Location.DOWN:
            if self.rect.y < self.intersection.y + self.intersection.height:
                self.rect.y += CAR_SPEED
            elif self.rect.y >= self.intersection.y + self.intersection.height:
                self.intersection = self.intersection.neighbours["bottom"]
                if self.intersection is not None:
                    self.init_location = Location.UP
                    self._choose_path()
                    self._position()
        if self.final_location == Location.LEFT:
            if (
                self.rect.y
                < self.intersection.y + self.intersection.height // 2 - CAR_WIDTH
            ):
                self.rect.y += CAR_SPEED
                if (
                    self.rect.y
                    >= self.intersection.y + self.intersection.height // 2 - CAR_WIDTH
                ):
                    self.rect.x = (
                        self.intersection.x + self.intersection.width // 2 - CAR_WIDTH
                    )
                    self.orientation = Orientation.HORIZONTAL
            elif self.rect.x > self.intersection.x - CAR_WIDTH:
                self.rect.x -= CAR_SPEED
                if self.rect.x <= self.intersection.x - CAR_WIDTH:
                    self.intersection = self.intersection.neighbours["left"]
                    if self.intersection is not None:
                        self.init_location = Location.RIGHT
                        self._choose_path()
                        self._position()
        for car in car_list:
            if self.orientation == Orientation.HORIZONTAL:
                gap_rect = pygame.Rect(self.rect.x, self.rect.y, CAR_WIDTH + 5, CAR_HEIGHT)
            else:
                gap_rect = pygame.Rect(self.rect.x, self.rect.y, CAR_HEIGHT, CAR_WIDTH + 5)
            if car.id != self.id:
                if gap_rect.colliderect(car.rect):
                    self.rect.x = init_x
                    self.rect.y = init_y

    def _move_from_right(self, car_list):
        init_x = self.rect.x
        init_y = self.rect.y
        if (
            self.intersection.lights[1] == "red"
            and self.rect.x - CAR_SPEED
            < self.intersection.x + (self.intersection.width + ROAD_WIDTH) // 2 + 2 * 5
            and self.rect.x - CAR_SPEED
            > self.intersection.x
            + (self.intersection.width + ROAD_WIDTH) // 2
            + 2 * 5
            - CAR_WIDTH
        ):
            return
        if self.final_location == Location.DOWN:
            if (
                self.rect.x
                > self.intersection.x
                + (
                    self.intersection.width
                    - ROAD_WIDTH // 2
                    - LINE_WIDTH // 2
                    - CAR_WIDTH // 2
                )
                // 2
            ):
                self.rect.x -= CAR_SPEED
                if (
                    self.rect.x
                    <= self.intersection.x
                    + (
                        self.intersection.width
                        - ROAD_WIDTH // 2
                        - LINE_WIDTH // 2
                        - CAR_WIDTH // 2
                    )
                    // 2
                ):
                    self.rect.x = (
                        self.intersection.x
                        + (
                            self.intersection.width
                            - ROAD_WIDTH // 2
                            - LINE_WIDTH // 2
                            - CAR_WIDTH // 2
                        )
                        // 2
                    )
                    self.orientation = Orientation.VERTICAL
            elif self.rect.y < self.intersection.y + self.intersection.height:
                self.rect.y += CAR_SPEED
                if self.rect.y >= self.intersection.y + self.intersection.height:
                    self.intersection = self.intersection.neighbours["bottom"]
                    if self.intersection is not None:
                        self.init_location = Location.UP
                        self._choose_path()
                        self._position()
        if self.final_location == Location.LEFT:
            if self.rect.x > self.intersection.x - CAR_WIDTH:
                self.rect.x -= CAR_SPEED
            elif self.rect.x <= self.intersection.x - CAR_WIDTH:
                self.intersection = self.intersection.neighbours["left"]
                if self.intersection is not None:
                    self.init_location = Location.RIGHT
                    self._choose_path()
                    self._position()
        if self.final_location == Location.UP:
            if (
                self.rect.x
                > self.intersection.x
                + (
                    self.intersection.width
                    + ROAD_WIDTH // 2
                    + LINE_WIDTH // 2
                    - CAR_WIDTH // 2
                )
                // 2
            ):
                self.rect.x -= CAR_SPEED
                if (
                    self.rect.x
                    <= self.intersection.x
                    + (
                        self.intersection.width
                        + ROAD_WIDTH // 2
                        + LINE_WIDTH // 2
                        - CAR_WIDTH // 2
                    )
                    // 2
                ):
                    self.rect.y = (
                        self.intersection.y + self.intersection.height // 2 - CAR_WIDTH
                    )
                    self.orientation = Orientation.VERTICAL
            elif self.rect.y > self.intersection.y - CAR_WIDTH:
                self.rect.y -= CAR_SPEED
                if self.rect.y <= self.intersection.y - CAR_WIDTH:
                    self.intersection = self.intersection.neighbours["top"]
                    if self.intersection is not None:
                        self.init_location = Location.DOWN
                        self._choose_path()
                        self._position()
        for car in car_list:
            if self.orientation == Orientation.HORIZONTAL:
                gap_rect = pygame.Rect(self.rect.x, self.rect.y, CAR_WIDTH + 5, CAR_HEIGHT)
            else:
                gap_rect = pygame.Rect(self.rect.x, self.rect.y, CAR_HEIGHT, CAR_WIDTH + 5)
            if car.id != self.id:
                if gap_rect.colliderect(car.rect):
                    self.rect.x = init_x
                    self.rect.y = init_y

    def _move_from_down(self, car_list):
        init_x = self.rect.x
        init_y = self.rect.y
        if (
            self.intersection.lights[2] == "red"
            and self.rect.y - CAR_SPEED
            < self.intersection.y + (self.intersection.height + ROAD_WIDTH) // 2 + 2 * 5
            and self.rect.y - CAR_SPEED
            > self.intersection.y
            + (self.intersection.height + ROAD_WIDTH) // 2
            - 2 * 5
            - CAR_WIDTH
        ):
            return
        if self.final_location == Location.LEFT:
            if (
                self.rect.y
                > self.intersection.y
                + (
                    self.intersection.height
                    - ROAD_WIDTH // 2
                    - LINE_WIDTH // 2
                    - CAR_WIDTH // 2
                )
                // 2
            ):
                self.rect.y -= CAR_SPEED
                if (
                    self.rect.y
                    <= self.intersection.y
                    + (
                        self.intersection.height
                        - ROAD_WIDTH // 2
                        - LINE_WIDTH // 2
                        - CAR_WIDTH // 2
                    )
                    // 2
                ):
                    self.rect.y = (
                        self.intersection.y
                        + (
                            self.intersection.height
                            - ROAD_WIDTH // 2
                            - LINE_WIDTH // 2
                            - CAR_WIDTH // 2
                        )
                        // 2
                    )
                    self.orientation = Orientation.HORIZONTAL
            elif self.rect.x > self.intersection.x - CAR_WIDTH:
                self.rect.x -= CAR_SPEED
                if self.rect.x <= self.intersection.x - CAR_WIDTH:
                    self.intersection = self.intersection.neighbours["left"]
                    if self.intersection is not None:
                        self.init_location = Location.RIGHT
                        self._choose_path()
                        self._position()
        if self.final_location == Location.UP:
            if self.rect.y > self.intersection.y - CAR_WIDTH:
                self.rect.y -= CAR_SPEED
            elif self.rect.y <= self.intersection.y - CAR_WIDTH:
                self.intersection = self.intersection.neighbours["top"]
                if self.intersection is not None:
                    self.init_location = Location.DOWN
                    self._choose_path()
                    self._position()
        if self.final_location == Location.RIGHT:
            if (
                self.rect.y
                > self.intersection.y
                + (
                    self.intersection.height
                    + ROAD_WIDTH // 2
                    + LINE_WIDTH // 2
                    - CAR_WIDTH // 2
                )
                // 2
            ):
                self.rect.y -= CAR_SPEED
                if (
                    self.rect.y
                    <= self.intersection.y
                    + (
                        self.intersection.height
                        + ROAD_WIDTH // 2
                        + LINE_WIDTH // 2
                        - CAR_WIDTH // 2
                    )
                    // 2
                ):
                    self.rect.x = (
                        self.intersection.x
                        + self.intersection.width // 2
                        + CAR_WIDTH // 2
                    )
                    self.orientation = Orientation.HORIZONTAL
            elif self.rect.x < self.intersection.x + self.intersection.width:
                self.rect.x += CAR_SPEED
                if self.rect.x >= self.intersection.x + self.intersection.width:
                    self.intersection = self.intersection.neighbours["right"]
                    if self.intersection is not None:
                        self.init_location = Location.LEFT
                        self._choose_path()
                        self._position()
                        
        for car in car_list:
            if self.orientation == Orientation.HORIZONTAL:
                gap_rect = pygame.Rect(self.rect.x, self.rect.y, CAR_WIDTH + 5, CAR_HEIGHT)
            else:
                gap_rect = pygame.Rect(self.rect.x, self.rect.y, CAR_HEIGHT, CAR_WIDTH + 5)
            if car.id != self.id:
                if gap_rect.colliderect(car.rect):
                    self.rect.x = init_x
                    self.rect.y = init_y

    def _move_from_left(self, car_list):
        init_x = self.rect.x
        init_y = self.rect.y
        if (
            self.intersection.lights[3] == "red"
            and self.rect.x + CAR_SPEED
            > self.intersection.x
            + (self.intersection.width - ROAD_WIDTH) // 2
            - 2 * 5
            - CAR_WIDTH
            and self.rect.x + CAR_SPEED
            < self.intersection.x + (self.intersection.width - ROAD_WIDTH) // 2 - 2 * 5
        ):
            return
        if self.final_location == Location.UP:
            if (
                self.rect.x
                < self.intersection.x
                + (
                    self.intersection.width
                    + ROAD_WIDTH // 2
                    + LINE_WIDTH // 2
                    - CAR_WIDTH // 2
                )
                // 2
            ):
                self.rect.x += CAR_SPEED
                if (
                    self.rect.x
                    >= self.intersection.x
                    + (
                        self.intersection.width
                        + ROAD_WIDTH // 2
                        + LINE_WIDTH // 2
                        - CAR_WIDTH // 2
                    )
                    // 2
                ):
                    self.rect.x = (
                        self.intersection.x
                        + (
                            self.intersection.width
                            + ROAD_WIDTH // 2
                            + LINE_WIDTH // 2
                            - CAR_WIDTH // 2
                        )
                        // 2
                    )
                    self.orientation = Orientation.VERTICAL
            elif self.rect.y > self.intersection.y - CAR_WIDTH:
                self.rect.y -= CAR_SPEED
                if self.rect.y <= self.intersection.y - CAR_WIDTH:
                    self.intersection = self.intersection.neighbours["top"]
                    if self.intersection is not None:
                        self.init_location = Location.DOWN
                        self._choose_path()
                        self._position()
        if self.final_location == Location.RIGHT:
            if self.rect.x < self.intersection.x + self.intersection.width:
                self.rect.x += CAR_SPEED
            elif self.rect.x >= self.intersection.x + self.intersection.width:
                self.intersection = self.intersection.neighbours["right"]
                if self.intersection is not None:
                    self.init_location = Location.LEFT
                    self._choose_path()
                    self._position()
        if self.final_location == Location.DOWN:
            if (
                self.rect.x
                < self.intersection.x
                + (
                    self.intersection.width
                    - ROAD_WIDTH // 2
                    - LINE_WIDTH // 2
                    - CAR_WIDTH // 2
                )
                // 2
            ):
                self.rect.x += CAR_SPEED
                if (
                    self.rect.x
                    >= self.intersection.x
                    + (
                        self.intersection.width
                        - ROAD_WIDTH // 2
                        - LINE_WIDTH // 2
                        - CAR_WIDTH // 2
                    )
                    // 2
                ):
                    self.rect.x = (
                        self.intersection.x
                        + (
                            self.intersection.width
                            - ROAD_WIDTH // 2
                            - LINE_WIDTH // 2
                            - CAR_WIDTH // 2
                        )
                        // 2
                    )
                    self.orientation = Orientation.VERTICAL
            elif self.rect.y < self.intersection.y + self.intersection.height:
                self.rect.y += CAR_SPEED
                if self.rect.y >= self.intersection.y + self.intersection.height:
                    self.intersection = self.intersection.neighbours["bottom"]
                    if self.intersection is not None:
                        self.init_location = Location.UP
                        self._choose_path()
                        self._position()
        for car in car_list:
            if self.orientation == Orientation.HORIZONTAL:
                gap_rect = pygame.Rect(self.rect.x, self.rect.y, CAR_WIDTH + 5, CAR_HEIGHT)
            else:
                gap_rect = pygame.Rect(self.rect.x, self.rect.y, CAR_HEIGHT, CAR_WIDTH + 5)
            if car.id != self.id:
                if gap_rect.colliderect(car.rect):
                    self.rect.x = init_x
                    self.rect.y = init_y

    def move(self, car_list):
        if self.init_location == Location.UP:
            self._move_from_up(car_list)
        elif self.init_location == Location.RIGHT:
            self._move_from_right(car_list)
        elif self.init_location == Location.DOWN:
            self._move_from_down(car_list)
        elif self.init_location == Location.LEFT:
            self._move_from_left(car_list)

