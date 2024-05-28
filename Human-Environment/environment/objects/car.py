import random
import time
import uuid
import pygame

from ..colors import RED, GREEN
from ..constants import (
    CAR_SPEED,
    CAR_WIDTH,
    CAR_HEIGHT,
    LINE_WIDTH,
    ROAD_WIDTH,
    Location,
    Orientation,
)
from ..objects.intersection import Intersection


class Car:
    def __init__(self, init_location, final_location, intersection):
        self.id = uuid.uuid1()
        self.time_spent = 0
        self.reward = 0.5
        self.color = RED
        self.init_location = init_location
        self.final_location = final_location
        self.intersection: Intersection = intersection
        self._set_orientation()
        if self.orientation == Orientation.E or self.orientation == Orientation.W:
            self.rect = pygame.Rect(0, 0, CAR_WIDTH, CAR_HEIGHT)
        if self.orientation == Orientation.N or self.orientation == Orientation.S:
            self.rect = pygame.Rect(0, 0, CAR_HEIGHT, CAR_WIDTH)
        self._position()
        self._set_life()

    def _set_orientation(self):
        if self.init_location == Location.UP:
            self.orientation = Orientation.S
        elif self.init_location == Location.RIGHT:
            self.orientation = Orientation.W
        elif self.init_location == Location.DOWN:
            self.orientation = Orientation.N
        elif self.init_location == Location.LEFT:
            self.orientation = Orientation.E

    def _change_orientation(self):
        if self.final_location == Location.UP:
            self.orientation = Orientation.N
        elif self.final_location == Location.RIGHT:
            self.orientation = Orientation.E
        elif self.final_location == Location.DOWN:
            self.orientation = Orientation.S
        elif self.final_location == Location.LEFT:
            self.orientation = Orientation.W

        if self.orientation == Orientation.N or self.orientation == Orientation.S:
            self.rect.width = CAR_HEIGHT
            self.rect.height = CAR_WIDTH
        if self.orientation == Orientation.E or self.orientation == Orientation.W:
            self.rect.width = CAR_WIDTH
            self.rect.height = CAR_HEIGHT

    def _set_life(self):
        random_number = random.randint(1, 4)
        self.life = random_number * 40
        
    def _drain_life(self):
        self.time_spent += 1
        self.reward -= self.time_spent / 10_000
        self.life -= 1

    def _position(self):
        self.crossed = False
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

    def draw(self, window, view_collision=False):

        pygame.draw.rect(
            window,
            self.color,
            self.rect,
        )
        if view_collision:
            pygame.draw.rect(
                window,
                GREEN,
                self.col_rect,
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

    def _check_collision(self, init_x, init_y, car_list):
        if self.orientation == Orientation.N:
            self.col_rect = pygame.Rect(self.rect.x, self.rect.y - 5, CAR_HEIGHT, 5)
        elif self.orientation == Orientation.E:
            self.col_rect = pygame.Rect(
                self.rect.x + CAR_WIDTH, self.rect.y, 5, CAR_HEIGHT
            )
        elif self.orientation == Orientation.S:
            self.col_rect = pygame.Rect(
                self.rect.x, self.rect.y + CAR_WIDTH, CAR_HEIGHT, 5
            )
        elif self.orientation == Orientation.W:
            self.col_rect = pygame.Rect(self.rect.x - 5, self.rect.y, 5, CAR_HEIGHT)
        for car in car_list:
            if self.id != car.id and car.rect.colliderect(self.rect):
                print(f"Hit car at {self.intersection.id}")
            if car.rect.colliderect(self.col_rect):
                self._drain_life()
                self.rect.x = init_x
                self.rect.y = init_y
                break

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
            < self.intersection.y
            + (self.intersection.height - ROAD_WIDTH) // 2
            - 2 * 5
            - CAR_WIDTH
            + CAR_SPEED
        ):
            self._drain_life()
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
                    self._change_orientation()
                    self.crossed = True
                    # self._increase_life()
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
                if self.rect.y > (self.intersection.y + self.intersection.height) // 2:
                    self.crossed = True
            elif self.rect.y >= self.intersection.y + self.intersection.height:            
                # self._increase_life()
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
                    self._change_orientation()
                    self.crossed = True
                    # self._increase_life()
            elif self.rect.x > self.intersection.x - CAR_WIDTH:
                self.rect.x -= CAR_SPEED
                if self.rect.x <= self.intersection.x - CAR_WIDTH:
                    self.intersection = self.intersection.neighbours["left"]
                    if self.intersection is not None:
                        self.init_location = Location.RIGHT
                        self._choose_path()
                        self._position()

        self._check_collision(init_x, init_y, car_list)

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
            - CAR_SPEED
        ):
            self._drain_life()
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
                    self._change_orientation()
                    self.crossed = True
                    # self._increase_life()
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
                if self.rect.x <= (self.intersection.x - CAR_WIDTH) // 2:
                    self.crossed = True
            elif self.rect.x <= self.intersection.x - CAR_WIDTH:
                self.intersection = self.intersection.neighbours["left"]
                # self._increase_life()
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
                    self._change_orientation()
                    self.crossed = True
                    # self._increase_life()
            elif self.rect.y > self.intersection.y - CAR_WIDTH:
                self.rect.y -= CAR_SPEED
                if self.rect.y <= self.intersection.y - CAR_WIDTH:
                    self.intersection = self.intersection.neighbours["top"]
                    if self.intersection is not None:
                        self.init_location = Location.DOWN
                        self._choose_path()
                        self._position()

        self._check_collision(init_x, init_y, car_list)

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
            - CAR_SPEED
        ):
            self._drain_life()
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
                    self._change_orientation()
                    self.crossed = True
                    # self._increase_life()
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
                if self.rect.y <= (self.intersection.y - CAR_WIDTH) // 2:
                    self.crossed = True
            elif self.rect.y <= self.intersection.y - CAR_WIDTH:
                self.intersection = self.intersection.neighbours["top"]
                # self._increase_life()
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
                    self._change_orientation()
                    self.crossed = True
                    # self._increase_life()
            elif self.rect.x < self.intersection.x + self.intersection.width:
                self.rect.x += CAR_SPEED
                if self.rect.x >= self.intersection.x + self.intersection.width:
                    self.intersection = self.intersection.neighbours["right"]
                    if self.intersection is not None:
                        self.init_location = Location.LEFT
                        self._choose_path()
                        self._position()

        self._check_collision(init_x, init_y, car_list)

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
            < self.intersection.x
            + (self.intersection.width - ROAD_WIDTH) // 2
            - 2 * 5
            - CAR_WIDTH
            + CAR_SPEED
        ):
            self._drain_life()
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
                    self._change_orientation()
                    self.crossed = True
                    # # self._increase_life()
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
                if self.rect.x >= (self.intersection.x + self.intersection.width) // 2:
                    self.crossed = True
            elif self.rect.x >= self.intersection.x + self.intersection.width:
                self.intersection = self.intersection.neighbours["right"]
                # # self._increase_life()
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
                    self._change_orientation()
                    self.crossed = True
                    # # self._increase_life()
            elif self.rect.y < self.intersection.y + self.intersection.height:
                self.rect.y += CAR_SPEED
                if self.rect.y >= self.intersection.y + self.intersection.height:
                    self.intersection = self.intersection.neighbours["bottom"]
                    if self.intersection is not None:
                        self.init_location = Location.UP
                        self._choose_path()
                        self._position()

        self._check_collision(init_x, init_y, car_list)

    def move(self, car_list):
        if self.init_location == Location.UP:
            self._move_from_up(car_list)
        elif self.init_location == Location.RIGHT:
            self._move_from_right(car_list)
        elif self.init_location == Location.DOWN:
            self._move_from_down(car_list)
        elif self.init_location == Location.LEFT:
            self._move_from_left(car_list)
