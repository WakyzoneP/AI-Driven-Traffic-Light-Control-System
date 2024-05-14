import pygame
from colors import GRAY
from constants import LINE_LENGTH, LINE_SPACING, ROAD_LENGTH, ROAD_WIDTH


class Road:
    def __init__(self, x, y, orientation, w=ROAD_WIDTH, h=ROAD_LENGTH):
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.color = GRAY
        self.orientation = orientation

    def draw(self, window):
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.height))
        for i in range(0, (self.height - 2 * LINE_SPACING) // (LINE_SPACING + LINE_LENGTH) + 1):
            pygame.draw.rect(
                window,
                (255, 255, 255),
                (self.x + (self.width - LINE_LENGTH) // 2, self.y + i * (LINE_SPACING + LINE_LENGTH), LINE_LENGTH, LINE_SPACING),
            )
