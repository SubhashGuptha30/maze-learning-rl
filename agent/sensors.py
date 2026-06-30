import math

import pygame

import config


class SensorSystem:
    def __init__(self, sensor_angles=None, max_range=config.MAX_SENSOR_RANGE, step_size=config.SENSOR_STEP):
        self.sensor_angles = sensor_angles if sensor_angles is not None else config.SENSOR_ANGLES
        self.max_range = max_range
        self.step_size = step_size
        self.readings = []
        self.hit_points = []

    def cast_ray(self, agent, maze, relative_angle):
        ray_angle = agent.angle + relative_angle
        # Sensor origin is at the front of the agent
        start_x = agent.x + agent.radius * math.cos(agent.angle)
        start_y = agent.y + agent.radius * math.sin(agent.angle)
        distance = 0
        hit_point = None

        while distance < self.max_range:
            x = start_x + distance * math.cos(ray_angle)
            y = start_y + distance * math.sin(ray_angle)

            row, column = maze.world_to_grid(x, y)
            if maze.is_wall(row, column):
                hit_point = (x, y)
                break

            distance += self.step_size

        if hit_point is None:
            distance = self.max_range
            hit_point = (start_x + self.max_range * math.cos(ray_angle), start_y + self.max_range * math.sin(ray_angle))

        return distance, hit_point

    def update(self, agent, maze):
        self.readings = []
        self.hit_points = []

        for relative_angle in self.sensor_angles:
            distance, hit_point = self.cast_ray(agent, maze, relative_angle)
            self.readings.append(distance / self.max_range)
            self.hit_points.append(hit_point)

    def draw(self, screen, agent):
        start_x = int(agent.x + agent.radius * math.cos(agent.angle))
        start_y = int(agent.y + agent.radius * math.sin(agent.angle))
        for hit_point in self.hit_points:
            pygame.draw.line(screen, config.YELLOW, (start_x, start_y), (int(hit_point[0]), int(hit_point[1])), 1)
            pygame.draw.circle(screen, config.YELLOW, (int(hit_point[0]), int(hit_point[1])), 2)

    def get_readings(self):
        return self.readings
