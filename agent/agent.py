import math

import pygame

from agent.movement import Movement
from agent.sensors import SensorSystem


class Agent:
    def __init__(self, agent_id, x, y, angle=0.0, radius=10, speed=2.5, alive=True, color=(255, 0, 0), movement=None, sensors=None):
        self.id = agent_id
        self.x = float(x)
        self.y = float(y)
        self.angle = float(angle)
        self.radius = radius
        self.speed = float(speed)
        self.alive = alive
        self.color = color
        self.movement = movement if movement is not None else Movement()
        self.sensors = sensors if sensors is not None else SensorSystem()

    def set_movement(self, movement):
        self.movement = movement

    def turn_left(self):
        self.movement.turn_left(self)

    def turn_right(self):
        self.movement.turn_right(self)

    def move_forward(self, maze):
        self.movement.move_forward(self, maze)

    def move_backward(self, maze):
        self.movement.move_backward(self, maze)

    def draw(self, screen):
        if not self.alive:
            return

        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        tip_x = self.x + (self.radius + 6) * math.cos(self.angle)
        tip_y = self.y + (self.radius + 6) * math.sin(self.angle)
        pygame.draw.line(screen, (255, 255, 255), (int(self.x), int(self.y)), (int(tip_x), int(tip_y)), 2)
