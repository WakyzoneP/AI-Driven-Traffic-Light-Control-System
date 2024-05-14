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

# font = pygame.font.Font('arial.ttf', 25)

class Environment:
    def __init__(self, w=WINDOW_WIDTH, h=WINDOW_HEIGHT):
        self.view_collision = False
        self.time = 100
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
        
        self.health = 20000

        self.car_list = []
        # self.car_list.append(Car(Location.UP, Location.DOWN, self.intersections[0]))
        # self.car_list.append(Car(Location.RIGHT, Location.DOWN, self.intersections[0]))
        # self.car_list.append(Car(Location.DOWN, Location.RIGHT, self.intersections[0]))
        # self.car_list.append(Car(Location.LEFT, Location.RIGHT, self.intersections[1]))
        # self.car_list.append(Car(Location.UP, Location.LEFT, self.intersections[1]))
        # self.car_list.append(Car(Location.UP, Location.LEFT, self.intersections[1]))

    def draw_background(self):
        self.window.fill(BLACK)
        for interaction in self.intersections:
            interaction.draw(self.window)
            
    def _draw_health(self):
        pass
        # text = font.render(f"Health: {self.health}", True, (255, 255, 255))
        # self.window.blit(text, (10, 10))

    def update_ui(self):
        self.draw_background()
        for car in self.car_list:
            car.draw(self.window, self.view_collision)
        self._draw_health()
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
                if event.key == pygame.K_c:
                    self.view_collision = not self.view_collision

        random_number = random.randint(0, 100)
        if random_number == 10:
            print(f"new car - {self.car_list.__len__()}")
            random_intersection = random.choice(self.intersections)
            spawn_locations_list = []
            for neighbour in random_intersection.neighbours:
                if random_intersection.neighbours[neighbour] is None:
                    if neighbour == "top":
                        spawn_locations_list.append(Location.UP)
                    elif neighbour == "right":
                        spawn_locations_list.append(Location.RIGHT)
                    elif neighbour == "bottom":
                        spawn_locations_list.append(Location.DOWN)
                    elif neighbour == "left":
                        spawn_locations_list.append(Location.LEFT)
            init_location = random.choice(spawn_locations_list)
            final_locations = [
                location for location in Location if location != init_location
            ]
            final_location = random.choice(final_locations)
            new_car = Car(init_location, final_location, random_intersection)
            is_valid = True
            for car in self.car_list:
                if car.rect.colliderect(new_car.rect):
                    print("Cannot spawn car, intersection is occupied.")
                    is_valid = False
                    break
            if is_valid:
                self.car_list.append(new_car)

        self.time -= 1
        if self.time == 0:
            self.time = 100
            # self.car_list.append(Car(Location.UP, Location.LEFT, self.intersections[1]))
            # self.car_list.append(Car(Location.LEFT, Location.RIGHT, self.intersections[1]))
            # self.car_list.append(Car(Location.UP, Location.LEFT, self.intersections[1]))
            # self.car_list.append(Car(Location.UP, Location.RIGHT, self.intersections[2]))

        # print(f"{self.car_list[0].intersection.id} - {self.car_list[0].init_location} - {self.car_list[0].orientation} - {self.car_list[0].final_location}")

        for car in self.car_list:
            if car.intersection is None:
                self.car_list.remove(car)
            else:
                car.move(self.car_list)

        self.update_ui()
        self.clock.tick(FPS)


if __name__ == "__main__":
    env = Environment()
    while True:
        env.step()
