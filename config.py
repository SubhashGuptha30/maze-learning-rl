import math

# Window and Game Loop Settings
FPS = 60
WINDOW_TITLE = "NeuroEvolution Maze"

# Maze Settings
CELL_SIZE = 40

# Agent Settings
AGENT_RADIUS = 10
AGENT_SPEED = 2.5
TURN_SPEED = math.radians(5)
HEADING_LENGTH = 6

# Sensor Settings
MAX_SENSOR_RANGE = 200
SENSOR_STEP = 1
SENSOR_ANGLES = [-math.pi / 2, -math.pi / 4, 0.0, math.pi / 4, math.pi / 2]

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
