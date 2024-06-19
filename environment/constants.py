from enum import Enum


WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 1000
FPS = 60

TOP_LEFT = (50, 50)

INTERSECTION_WIDTH = 200
INTERSECTION_HEIGHT = 200

ROAD_WIDTH = 50
LIGHT_WIDTH = 3

LINE_WIDTH = 5
LINE_LENGTH = 15
LINE_SPACING = 5

CAR_WIDTH = 20
CAR_HEIGHT = 10
CAR_SPEED = 1

CAR_SPAWN_RATE = 15
STEP_TIME = 200
ENV_HEALTH = 350

class Location(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3
    
class Orientation(Enum):
    N = 0
    E = 1
    S = 2
    W = 3
    
class EnvType(Enum):
    SIMULATION = 0
    TRAINING = 1