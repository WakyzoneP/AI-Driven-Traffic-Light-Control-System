import random
import pygame

from colors import BLACK
from constants import (
    INTERSECTION_HEIGHT,
    TOP_LEFT,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    FPS,
    Location,
)
from objects.car import Car
from objects.intersection import Intersection


class Environment:
    def __init__(self, w=WINDOW_WIDTH, h=WINDOW_HEIGHT):
        self.width = w
        self.height = h
        self.window = pygame.display.set_mode((w, h))
        pygame.display.set_caption("Environment Simulation")
        self.clock = pygame.time.Clock()
        self.intersections = []
        self.intersections.append(Intersection(TOP_LEFT[0], TOP_LEFT[1]))
        self.intersections.append(
            Intersection(TOP_LEFT[0] + INTERSECTION_HEIGHT, TOP_LEFT[1])
        )
        self.intersections.append(
            Intersection(TOP_LEFT[0], TOP_LEFT[1] + INTERSECTION_HEIGHT)
        )
        self.intersections[0].set_neighbours(
            {
                "top": None,
                "right": self.intersections[1],
                "bottom": self.intersections[2],
                "left": None,
            }
        )
        self.intersections[1].set_neighbours(
            {"top": None, "right": None, "bottom": None, "left": self.intersections[0]}
        )
        self.intersections[2].set_neighbours(
            {"top": self.intersections[0], "right": None, "bottom": None, "left": None}
        )

        self.car_list = []
        self.car_list.append(Car(Location.RIGHT, Location.UP, self.intersections[0]))

    def draw_background(self):
        self.window.fill(BLACK)
        for interaction in self.intersections:
            interaction.draw(self.window)

    def update_ui(self):
        self.draw_background()
        for car in self.car_list:
            car.draw(self.window)

        pygame.display.update()

    def step(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.intersections[0].change_light(0)
                if event.key == pygame.K_d:
                    self.intersections[0].change_light(1)
                if event.key == pygame.K_s:
                    self.intersections[0].change_light(2)
                if event.key == pygame.K_a:
                    self.intersections[0].change_light(3)
                if event.key == pygame.K_t:
                    self.intersections[1].change_light(0)
                if event.key == pygame.K_h:
                    self.intersections[1].change_light(1)
                if event.key == pygame.K_g:
                    self.intersections[1].change_light(2)
                if event.key == pygame.K_f:
                    self.intersections[1].change_light(3)
                if event.key == pygame.K_i:
                    self.intersections[2].change_light(0)
                if event.key == pygame.K_l:
                    self.intersections[2].change_light(1)
                if event.key == pygame.K_k:
                    self.intersections[2].change_light(2)
                if event.key == pygame.K_j:
                    self.intersections[2].change_light(3)
        
        random_number = random.randint(0, 100)
        if random_number == 10:
            random_init_location = random.choice(list(Location))
            random_final_location = random.choice([loc for loc in list(Location) if loc != random_init_location])
            
            self.car_list.append(Car(random_init_location, random_final_location, self.intersections[0]))

        for car in self.car_list:
            if car.intersection is None:
                self.car_list.remove(car)
            else:
                car.move()

        self.update_ui()
        self.clock.tick(FPS)


if __name__ == "__main__":
    env = Environment()
    while True:
        env.step()
