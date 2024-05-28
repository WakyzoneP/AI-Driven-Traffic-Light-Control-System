import random
import pygame
import numpy as np

from .colors import BLACK
from .constants import (
    INTERSECTION_HEIGHT,
    TOP_LEFT,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    FPS,
    Location,
    STEP_TIME,
)
from .objects.car import Car
from .objects.intersection import Intersection

pygame.init()
font = pygame.font.Font("arial.ttf", 25)

SPEED_INCREMENT = 1


class Environment:
    def __init__(self, w=WINDOW_WIDTH, h=WINDOW_HEIGHT):
        self.speed_increment = SPEED_INCREMENT
        self.can_change_time = STEP_TIME / self.speed_increment
        self.score = 0
        self.view_collision = False
        self.width = w
        self.height = h
        self.window = pygame.display.set_mode((w, h))
        pygame.display.set_caption("Environment Simulation")
        self.clock = pygame.time.Clock()
        self.intersections: list[Intersection] = []
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

        self.health = 2_000

        self.car_list: list[Car] = []
        # self.car_list.append(Car(Location.UP, Location.DOWN, self.intersections[0]))
        # self.car_list.append(Car(Location.RIGHT, Location.DOWN, self.intersections[0]))
        # self.car_list.append(Car(Location.DOWN, Location.RIGHT, self.intersections[0]))
        # self.car_list.append(Car(Location.LEFT, Location.RIGHT, self.intersections[1]))
        # self.car_list.append(Car(Location.UP, Location.LEFT, self.intersections[1]))
        # self.car_list.append(Car(Location.UP, Location.LEFT, self.intersections[1]))

    def _draw_background(self):
        self.window.fill(BLACK)
        for interaction in self.intersections:
            interaction.draw(self.window)

    def _increase_health(self, amount):
        self.health += amount

    def _update_ui(self):
        self._draw_background()
        for car in self.car_list:
            car.draw(self.window, self.view_collision)
        health_text = font.render(f"Health: {self.health}", True, (255, 255, 255))
        self.window.blit(health_text, (10, 10))
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.window.blit(score_text, (10, 40))
        pygame.display.update()

    def _manual_control(self):
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
                if event.key == pygame.K_z:
                    self.speed_increment = 1
                if event.key == pygame.K_x:
                    self.speed_increment = 100

    def _change_light(self, actions: list[int]):
        for i in range(len(actions)):
            action = actions[i]
            self.intersections[i].change_light(action)

    def _spawn_car_mechanism(self):
        random_number = random.randint(0, 50)
        if random_number == 10:
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
                return True
            else:
                return False
        return True

    def generate_state(self):
        # first row contains the sum of the life of the cars in the intersection
        # third row contains the health of the agent
        state = [0 for _ in range(12)]
        for car in self.car_list:
            if car.intersection is None:
                continue
            car_intersection_index = self.intersections.index(car.intersection)
            init_location = car.init_location
            final_location = car.final_location
            crossed = car.crossed
            if not crossed:
                if init_location == Location.UP:
                    state[car_intersection_index * 4] += car.life
                elif init_location == Location.RIGHT:
                    state[car_intersection_index * 4 + 1] += car.life
                elif init_location == Location.DOWN:
                    state[car_intersection_index * 4 + 2] += car.life
                elif init_location == Location.LEFT:
                    state[car_intersection_index * 4 + 3] += car.life
            else:
                if final_location == Location.UP:
                    state[car_intersection_index * 4] += car.life
                elif final_location == Location.RIGHT:
                    state[car_intersection_index * 4 + 1] += car.life
                elif final_location == Location.DOWN:
                    state[car_intersection_index * 4 + 2] += car.life
                elif final_location == Location.LEFT:
                    state[car_intersection_index * 4 + 3] += car.life
        # for intersection in self.intersections:
        #     for light in intersection.lights:
        #         if light == "red":
        #             state.append(0)
        #         else:
        #             state.append(1)
        state.append(self.health)

        return np.array(state, dtype=np.int32)

    def reset(self):
        self.score = 0
        self.health = 2_000
        self.car_list = []

    def can_make_step(self):
        return self.can_change_time == 0

    def run(self):
        self.health -= 1
        self.can_change_time -= 1
        self.reward = -0.005
        self._manual_control()
        could_spawn = self._spawn_car_mechanism()
        sum = 0
        for car in self.car_list:
            sum += car.reward
        self.reward += sum
        self.reward /= len(self.car_list) + 1
        for car in self.car_list:
            if car.intersection is None:
                self._increase_health(car.life)
                self.score += 1
                self.car_list.remove(car)
            else:
                car.move(self.car_list)

        if not could_spawn:
            self.health -= 100
            self.reward -= 1.25

        game_over = False
        if self.health < 0:
            game_over = True
            self.reward -= 1.25
            
        # if(self.reward < -2):
        #     self.reward = -2

        self._update_ui()
        self.clock.tick(FPS * self.speed_increment)

        return game_over, self.score
    
    def convert_to_base_4(self, num):
        base_4 = [0, 0, 0]
        for i in range(3):
            base_4[i] = num % 4
            num //= 4
        return base_4
    
    def convert_action(self, action: int):
        return self.convert_to_base_4(action)

    def step(self, action):
        action = self.convert_action(action)
        self.can_change_time = STEP_TIME
        self._change_light(action)

        return self.reward, self.score
