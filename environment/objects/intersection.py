import pygame

from ..colors import GRAY, WHITE


class Intersection:
    intersection_count = 0
    def __init__(self, x, y, width, height, road_width, light_width, line_width, line_length, line_spacing):
        Intersection.intersection_count += 1
        self.id = Intersection.intersection_count
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.road_width = road_width
        self.light_width = light_width
        self.line_width = line_width
        self.line_length = line_length
        self.line_spacing = line_spacing
        self.color = GRAY
        self.lights = ["red" for _ in range(4)]
        self.neighbours = {"top": None, "right": None, "bottom": None, "left": None}

    def _draw_lights(self, window):
        # North light
        pygame.draw.rect(
            window,
            self.lights[0],
            (
                self.x + (self.width - self.road_width) // 2,
                self.y + (self.height - self.road_width) // 2 - self.light_width,
                (self.road_width - self.line_width) // 2,
                self.light_width,
            ),
        )
        pygame.draw.rect(
            window,
            self.lights[1],
            (
                self.x + (self.width + self.road_width) // 2,
                self.y + (self.height - self.road_width) // 2,
                self.light_width,
                (self.road_width - self.line_width) // 2,
            ),
        )
        pygame.draw.rect(
            window,
            self.lights[2],
            (
                self.x + (self.width) // 2 + self.light_width,
                self.y + (self.height + self.road_width) // 2,
                (self.road_width - self.line_width) // 2,
                self.light_width,
            ),
        )
        pygame.draw.rect(
            window,
            self.lights[3],
            (
                self.x + (self.width - self.road_width) // 2 - self.light_width,
                self.y + (self.height) // 2 + self.light_width,
                self.light_width,
                (self.road_width - self.line_width) // 2,
            ),
        )

    def draw(self, window):
        pygame.draw.rect(
            window,
            self.color,
            (self.x + (self.width - self.road_width) // 2, self.y, self.road_width, self.height),
        )
        pygame.draw.rect(
            window,
            self.color,
            (self.x, self.y + (self.height - self.road_width) // 2, self.width, self.road_width),
        )
        for i in range(
            0, int((self.width - self.line_spacing) // (self.line_spacing + self.line_length)) + 1
        ):
            pygame.draw.rect(
                window,
                WHITE,
                (
                    self.x + (self.width - self.line_width) // 2,
                    self.y + i * (self.line_spacing + self.line_length),
                    self.line_width,
                    self.line_length,
                ),
            )
            pygame.draw.rect(
                window,
                WHITE,
                (
                    self.x + i * (self.line_spacing + self.line_length),
                    self.y + (self.height - self.line_width) // 2,
                    self.line_length,
                    self.line_width,
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