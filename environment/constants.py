from enum import Enum


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
FPS = 60

TOP_LEFT = (50, 50)
INTERSECTION_WIDTH = 350
INTERSECTION_HEIGHT = 350
ROAD_WIDTH = 100
ROAD_LENGTH = 140
LINE_WIDTH = 10
LINE_LENGTH = 30
LINE_SPACING = 10
CAR_WIDTH = 40
CAR_HEIGHT = 20
CAR_SPEED = 2

STEP_TIME = 150

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