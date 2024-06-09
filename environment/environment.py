import random
import pygame
import numpy as np

from .colors import BLACK
from .constants import (
    CAR_HEIGHT,
    CAR_SPEED,
    CAR_WIDTH,
    INTERSECTION_HEIGHT,
    INTERSECTION_WIDTH,
    LIGHT_WIDTH,
    LINE_LENGTH,
    LINE_SPACING,
    LINE_WIDTH,
    ROAD_WIDTH,
    TOP_LEFT,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    FPS,
    Location,
    STEP_TIME,
    EnvType,
    MAX_SPEED_INCREMENT,
    ENV_HEALTH,
)
from .objects.car import Car
from .objects.intersection import Intersection

pygame.init()
font = pygame.font.Font("arial.ttf", 25)


class Environment:
    def __init__(
        self,
        intersections_json,
        traffic_level=1,
        w=WINDOW_WIDTH,
        h=WINDOW_HEIGHT,
        show_ui=True,
        env_type=EnvType.TRAINING,
    ):
        self.env_type = env_type
        self.show_ui = show_ui
        self.speed_increment = 1 if show_ui else MAX_SPEED_INCREMENT
        self.can_change_time = STEP_TIME
        self.score = 0
        self.view_collision = False
        self.width = w
        self.height = h
        self.traffic_level = 1 if self.env_type == EnvType.TRAINING else traffic_level

        if self.show_ui:
            self.window = pygame.display.set_mode((w, h))
            pygame.display.set_caption("Environment Simulation")

        self.clock = pygame.time.Clock()
        self._create_intersections(intersections_json)

        self.passed_cars = 0
        self.faults = 0

        self.car_list: list[Car] = []
        self.car_list.append(
            Car(
                CAR_WIDTH * self.inhance,
                CAR_HEIGHT * self.inhance,
                Location.UP,
                Location.RIGHT,
                self.intersections[0],
                CAR_SPEED,
            )
        )

    def _create_intersections(self, intersections_json):
        number_of_intersections = len(intersections_json)

        matrix: list[list[int]] = np.zeros((1, 1), dtype=int)

        index = 1
        for intersection in intersections_json:
            x = intersection["X"]
            y = intersection["Y"]
            if matrix.shape[0] <= x:
                matrix = np.pad(matrix, ((0, x - matrix.shape[0] + 1), (0, 0)))
            if matrix.shape[1] <= y:
                matrix = np.pad(matrix, ((0, 0), (0, y - matrix.shape[1] + 1)))
            matrix[x][y] = index
            index += 1

        max_shape = max(matrix.shape)
        self.health = ENV_HEALTH * max_shape

        self.inhance = 0
        while max_shape * INTERSECTION_HEIGHT * self.inhance < self.height - 100:
            self.inhance += 1

        self.inhance -= 1

        print(self.inhance)

        self.intersections: list[Intersection] = [
            None for _ in range(number_of_intersections)
        ]

        for line in range(matrix.shape[0]):
            for column in range(matrix.shape[1]):
                if matrix[line][column] == 0:
                    continue
                x = TOP_LEFT[0] + (column) * INTERSECTION_HEIGHT * self.inhance
                y = TOP_LEFT[1] + (line) * INTERSECTION_HEIGHT * self.inhance
                intersection = Intersection(
                    x,
                    y,
                    INTERSECTION_WIDTH * self.inhance,
                    INTERSECTION_HEIGHT * self.inhance,
                    ROAD_WIDTH * self.inhance,
                    LIGHT_WIDTH * self.inhance,
                    LINE_WIDTH * self.inhance,
                    LINE_LENGTH * self.inhance,
                    LINE_SPACING * self.inhance,
                )
                self.intersections[matrix[line][column] - 1] = intersection

        print(self.intersections)

        for intersection in intersections_json:
            x = intersection["X"]
            y = intersection["Y"]
            neighbours = {
                "top": (
                    self.intersections[matrix[x - 1][y] - 1]
                    if x - 1 >= 0 and matrix[x - 1][y] != 0
                    else None
                ),
                "right": (
                    self.intersections[matrix[x][y + 1] - 1]
                    if y + 1 < matrix.shape[1] and matrix[x][y + 1] != 0
                    else None
                ),
                "bottom": (
                    self.intersections[matrix[x + 1][y] - 1]
                    if x + 1 < matrix.shape[0] and matrix[x + 1][y] != 0
                    else None
                ),
                "left": (
                    self.intersections[matrix[x][y - 1] - 1]
                    if y - 1 >= 0 and matrix[x][y - 1] != 0
                    else None
                ),
            }
            self.intersections[matrix[x][y] - 1].set_neighbours(neighbours)

    def _draw_background(self):
        self.window.fill(BLACK)
        for interaction in self.intersections:
            interaction.draw(self.window)

    def _update_ui(self):
        self._draw_background()
        for car in self.car_list:
            car.draw(self.window, self.view_collision)
        if self.env_type == EnvType.TRAINING:
            health_text = font.render(f"Health: {self.health}", True, (255, 255, 255))
            self.window.blit(health_text, (self.width - 150, 10))
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.window.blit(score_text, (10, 10))
        pygame.display.update()

    def _manual_control(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    self.view_collision = not self.view_collision
                if event.key == pygame.K_1:
                    self.speed_increment = 1
                if event.key == pygame.K_2:
                    self.speed_increment = 2
                if event.key == pygame.K_3:
                    self.speed_increment = 3

    def _change_light(self, actions: list[int]):
        for i in range(len(actions)):
            action = actions[i]
            self.intersections[i].change_light(action)

    def _get_spawn_locations(self):
        spawn_locations = []
        for intersection in self.intersections:
            for neighbour in intersection.neighbours:
                if intersection.neighbours[neighbour] is None:
                    if neighbour == "top":
                        spawn_locations.append((Location.UP, intersection))
                    elif neighbour == "right":
                        spawn_locations.append((Location.RIGHT, intersection))
                    elif neighbour == "bottom":
                        spawn_locations.append((Location.DOWN, intersection))
                    elif neighbour == "left":
                        spawn_locations.append((Location.LEFT, intersection))
        return spawn_locations

    def _spawn_car_mechanism(self):
        random_number = random.randint(0, 10 * self.traffic_level)
        if random_number == 10:
            spawn_locations_list = self._get_spawn_locations()
            init_location, intersection = random.choice(spawn_locations_list)
            final_locations = [
                location for location in Location if location != init_location
            ]
            final_location = random.choice(final_locations)
            new_car = Car(
                CAR_WIDTH * self.inhance,
                CAR_HEIGHT * self.inhance,
                init_location,
                final_location,
                intersection,
                CAR_SPEED,
            )
            is_valid = True
            for car in self.car_list:
                if car.rect.colliderect(new_car.rect):
                    is_valid = False
                    break
            if is_valid:
                self.car_list.append(new_car)

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

        return np.array(state, dtype=np.int32)

    def reset(self):
        self.health = ENV_HEALTH
        self.score = 0
        self.car_list = []

    def _check_game_over(self):
        if self.health <= 0:
            return True
        spawn_locations = self._get_spawn_locations()
        for location in spawn_locations:
            init_location, intersection = location
            new_car = Car(init_location, Location.UP, intersection)
            is_valid = True
            for car in self.car_list:
                if car.rect.colliderect(new_car.rect):
                    is_valid = False
                    break
            if is_valid:
                return False

        return True

    def run(self):
        if self.env_type == EnvType.TRAINING:
            self.health -= 2
        self.can_change_time -= 1
        self._manual_control()
        self._spawn_car_mechanism()
        for car in self.car_list:
            if car.intersection is None:
                self.score += 1
                self.health += car.life
                self.car_list.remove(car)
                self.passed_cars += 1
            else:
                car.move(self.car_list)

        game_over = False
        if self.health <= 0 and self.env_type == EnvType.TRAINING:
            game_over = True
            self.faults += 5

        if self.show_ui:
            self._update_ui()

        if self.env_type == EnvType.SIMULATION:
            self.clock.tick(FPS * self.speed_increment)

        return game_over

    def convert_to_base(self, base, num):
        base_list = [0 for _ in range(base)]
        for i in range(base):
            base_list[i] = num % 4
            num //= 4
        return base_list

    def _convert_action(self, action: int):
        return self.convert_to_base(len(self.intersections), action)

    def _reward_calculator(self):
        for car in self.car_list:
            if car.intersection is not None:
                self.faults += 0.04

        return 0.05 + self.passed_cars - self.faults
    
    def _reward_calculator1(self):
        sum_of_rewards = 0
        for car in self.car_list:
            if car.intersection is not None:
                sum_of_rewards += car.reward
                
        return sum_of_rewards + self.passed_cars * 0.1 - self.faults * 0.1

    def step(self, action):
        action = self._convert_action(action)
        self.can_change_time = STEP_TIME
        self._change_light(action)

        game_over = False

        while self.can_change_time > 0 and not game_over:
            game_over = self.run()

        reward = self._reward_calculator()
        self.passed_cars = 0
        self.faults = 0

        return reward, self.score, game_over
