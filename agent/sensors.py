import math

import pygame


class SensorSystem:
    def __init__(self, sensor_angles=None, max_range=200, step_size=1):
        self.sensor_angles = sensor_angles if sensor_angles is not None else [-math.pi / 2, -math.pi / 4, 0.0, math.pi / 4, math.pi / 2]
        self.max_range = max_range
        self.step_size = step_size
        self.readings = []
        self.hit_points = []

    def cast_ray(self, agent, maze, relative_angle):
        ray_angle = agent.angle + relative_angle
        start_x = agent.x
        start_y = agent.y
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
        for hit_point in self.hit_points:
            pygame.draw.line(screen, (255, 255, 0), (int(agent.x), int(agent.y)), (int(hit_point[0]), int(hit_point[1])), 1)
            pygame.draw.circle(screen, (255, 255, 0), (int(hit_point[0]), int(hit_point[1])), 2)

    def get_readings(self):
        return self.readings
