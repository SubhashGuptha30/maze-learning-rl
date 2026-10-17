import math

# Window and Game Loop Settings
FPS = 60
WINDOW_TITLE = "NeuroEvolution Maze"

# Maze Settings
CELL_SIZE = 40
GOAL_RADIUS = 15

# Agent Settings
AGENT_RADIUS = 10
AGENT_SPEED = 2.5
TURN_SPEED = math.radians(5)
HEADING_LENGTH = 6

# Sensor Settings
MAX_SENSOR_RANGE = 200
SENSOR_STEP = 1
SENSOR_ANGLES = [-math.pi / 2, -math.pi / 4, 0.0, math.pi / 4, math.pi / 2]

# Brain Settings
BRAIN_FRONT_THRESHOLD = 0.3
BRAIN_CLEAR_THRESHOLD = 0.6

# Network Architecture
NETWORK_INPUTS = 6   # 5 wall sensors + direction to the goal
NETWORK_HIDDEN = 8
NETWORK_OUTPUTS = 4  # forward, backward, left, right

# Evolution
POPULATION_SIZE = 50
GENERATIONS = 50
MAX_FRAMES = 1000        # frame limit per generation
LAYOUT_MAX_FRAMES = 2000 # random tracks/mazes: a lap takes 600-900 frames even for a hand-written driver
STUCK_FRAMES = 150       # stop an agent that hasn't got closer to the goal for this long
ELITE_COUNT = 2
TOURNAMENT_SIZE = 3
MUTATION_RATE = 0.1      # chance each gene is mutated
MUTATION_STRENGTH = 0.5  # std dev of the Gaussian noise

# Fitness
GOAL_BONUS = 1000.0
SPEED_BONUS = 500.0      # scaled by the fraction of frames left when the goal is reached

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
