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

    def _ray_color(self, normalized_distance):
        """Return a color based on how close the wall is.
        Near (< 0.3) = RED, Medium (0.3–0.6) = ORANGE, Far (> 0.6) = GREEN."""
        if normalized_distance < 0.3:
            return config.RED
        elif normalized_distance < 0.6:
            return config.ORANGE
        else:
            return config.GREEN

    def cast_ray(self, agent, maze, relative_angle):
        ray_angle = agent.angle + relative_angle
        ax, ay = agent.position
        # Sensor origin is at the front of the agent
        start_x = ax + agent.radius * math.cos(agent.angle)
        start_y = ay + agent.radius * math.sin(agent.angle)
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

        # Direction to the goal relative to the heading, 0..1 (0.25 = to the right).
        # Without it the network only sees walls and can't tell which turn leads to the goal.
        # shortcut: jumps 1 -> 0 when the goal is dead ahead; use sin/cos (2 inputs) if that hurts.
        goal_x, goal_y = maze.get_goal()
        relative = (math.atan2(goal_y - agent.y, goal_x - agent.x) - agent.angle) % math.tau
        self.readings.append(relative / math.tau)

    def draw(self, screen, agent):
        ax, ay = agent.position
        start_x = int(ax + agent.radius * math.cos(agent.angle))
        start_y = int(ay + agent.radius * math.sin(agent.angle))
        for i, hit_point in enumerate(self.hit_points):
            color = self._ray_color(self.readings[i])
            pygame.draw.line(screen, color, (start_x, start_y), (int(hit_point[0]), int(hit_point[1])), 1)
            pygame.draw.circle(screen, color, (int(hit_point[0]), int(hit_point[1])), 2)

    def get_readings(self):
        return self.readings
