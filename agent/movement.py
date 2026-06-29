import math


class Movement:
    def __init__(self, turn_speed=math.radians(5)):
        self.turn_speed = turn_speed

    def turn_left(self, agent):
        agent.angle -= self.turn_speed

    def turn_right(self, agent):
        agent.angle += self.turn_speed

    def move_forward(self, agent, maze, speed=None):
        distance = agent.speed if speed is None else speed
        next_x = agent.x + distance * math.cos(agent.angle)
        next_y = agent.y + distance * math.sin(agent.angle)
        if maze.is_walkable(next_x, next_y, agent.radius):
            agent.x = next_x
            agent.y = next_y

    def move_backward(self, agent, maze, speed=None):
        distance = agent.speed if speed is None else speed
        next_x = agent.x - distance * math.cos(agent.angle)
        next_y = agent.y - distance * math.sin(agent.angle)
        if maze.is_walkable(next_x, next_y, agent.radius):
            agent.x = next_x
            agent.y = next_y
