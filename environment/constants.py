from enum import Enum


WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 1000
FPS = 60

TOP_LEFT = (50, 50)

INHANCE_LIST = [6, 5, 4, 3, 2.5, 2.20, 1.80, 1, 1.2, 1.1, 1]

INTERSECTION_WIDTH = 80
INTERSECTION_HEIGHT = 80

ROAD_WIDTH = 20
LIGHT_WIDTH = 1

LINE_WIDTH = 2
LINE_LENGTH = 6
LINE_SPACING = 2

CAR_WIDTH = 8
CAR_HEIGHT = 4


CAR_SPEED = 2
STEP_TIME = 200
MAX_SPEED_INCREMENT = 30

ENV_HEALTH = 1_500

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