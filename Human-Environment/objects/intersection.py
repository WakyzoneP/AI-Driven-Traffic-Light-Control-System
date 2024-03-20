import pygame

from colors import GRAY, WHITE
from constants import (
    INTERSECTION_WIDTH,
    INTERSECTION_HEIGHT,
    ROAD_WIDTH,
    LINE_WIDTH,
    LINE_LENGTH,
    LINE_SPACING,
)


class Intersection:
    intersection_count = 0
    def __init__(self, x, y, w=INTERSECTION_WIDTH, h=INTERSECTION_HEIGHT):
        Intersection.intersection_count += 1
        self.id = Intersection.intersection_count
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.color = GRAY
        self.lights = ["red" for _ in range(4)]
        self.neighbours = {"top": None, "right": None, "bottom": None, "left": None}

    def _draw_lights(self, window):
        pygame.draw.rect(
            window,
            self.lights[0],
            (
                self.x + (self.width - ROAD_WIDTH) // 2,
                self.y + (self.height - ROAD_WIDTH) // 2 - 5,
                (ROAD_WIDTH - LINE_WIDTH) / 2,
                5,
            ),
        )
        pygame.draw.rect(
            window,
            self.lights[1],
            (
                self.x + (self.width + ROAD_WIDTH) // 2,
                self.y + (self.height - ROAD_WIDTH) // 2,
                5,
                (ROAD_WIDTH - LINE_WIDTH) / 2,
            ),
        )
        pygame.draw.rect(
            window,
            self.lights[2],
            (
                self.x + (self.width) // 2 + 5,
                self.y + (self.height + ROAD_WIDTH) // 2,
                (ROAD_WIDTH - LINE_WIDTH) / 2,
                5,
            ),
        )
        pygame.draw.rect(
            window,
            self.lights[3],
            (
                self.x + (self.width - ROAD_WIDTH) // 2 - 5,
                self.y + (self.height) // 2 + 5,
                5,
                (ROAD_WIDTH - LINE_WIDTH) / 2,
            ),
        )

    def draw(self, window):
        pygame.draw.rect(
            window,
            self.color,
            (self.x + (self.width - ROAD_WIDTH) // 2, self.y, ROAD_WIDTH, self.height),
        )
        pygame.draw.rect(
            window,
            self.color,
            (self.x, self.y + (self.height - ROAD_WIDTH) // 2, self.width, ROAD_WIDTH),
        )
        for i in range(
            0, (self.width - LINE_SPACING) // (LINE_SPACING + LINE_LENGTH) + 1
        ):
            pygame.draw.rect(
                window,
                WHITE,
                (
                    self.x + (self.width - LINE_WIDTH) // 2,
                    self.y + i * (LINE_SPACING + LINE_LENGTH),
                    LINE_WIDTH,
                    LINE_LENGTH,
                ),
            )
            pygame.draw.rect(
                window,
                WHITE,
                (
                    self.x + i * (LINE_SPACING + LINE_LENGTH),
                    self.y + (self.height - LINE_WIDTH) // 2,
                    LINE_LENGTH,
                    LINE_WIDTH,
                ),
            )
        self._draw_lights(window)

    def change_light(self, index):
        for i in range(4):
            self.lights[i] = "red"
        if self.lights[index] == "red":
            self.lights[index] = "green"
        else:
            self.lights[index] = "red"

    def set_neighbours(self, neighbours):
        self.neighbours = neighbours

    def generate_car(self):
        pass

    def __str__(self) -> str:
        return f"Intersection at ({self.x}, {self.y}) with lights {self.lights}"