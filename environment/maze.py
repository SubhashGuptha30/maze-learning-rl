import pygame

from environment.tile import Tile
from config import CELL_SIZE, BLACK, WHITE, GRAY, GREEN, BLUE


class Maze:
    def __init__(self):
        self.layout = [
            "################",
            "#S.............#",
            "#.#####.######.#",
            "#..............#",
            "#.#######.####.#",
            "#..............#",
            "#.#######.####.#",
            "#.............G#",
            "################",
        ]
        self.cell_size = CELL_SIZE
        self.rows = len(self.layout)
        self.columns = len(self.layout[0]) if self.layout else 0
        self.width = self.columns * self.cell_size
        self.height = self.rows * self.cell_size
        self.spawn = None
        self.goal = None
        self.find_special_tiles()

    def find_special_tiles(self):
        for row_index, row in enumerate(self.layout):
            for col_index, cell in enumerate(row):
                center_x = col_index * self.cell_size + self.cell_size // 2
                center_y = row_index * self.cell_size + self.cell_size // 2

                if cell == Tile.SPAWN:
                    self.spawn = (center_x, center_y)
                elif cell == Tile.GOAL:
                    self.goal = (center_x, center_y)

    def draw(self, screen):
        for row_index, row in enumerate(self.layout):
            for col_index, cell in enumerate(row):
                x = col_index * self.cell_size
                y = row_index * self.cell_size

                if cell == Tile.WALL:
                    color = GRAY
                elif cell == Tile.SPAWN:
                    color = BLUE
                elif cell == Tile.GOAL:
                    color = GREEN
                else:
                    color = WHITE

                pygame.draw.rect(screen, color, (x, y, self.cell_size, self.cell_size))
                pygame.draw.rect(screen, BLACK, (x, y, self.cell_size, self.cell_size), 1)

    def get_spawn(self):
        return self.spawn

    def get_goal(self):
        return self.goal

    def world_to_grid(self, x, y):
        row = int(y // self.cell_size)
        column = int(x // self.cell_size)
        return row, column

    def grid_to_world(self, row, column):
        x = column * self.cell_size + self.cell_size // 2
        y = row * self.cell_size + self.cell_size // 2
        return x, y

    def is_wall(self, row, column):
        if not (0 <= row < self.rows and 0 <= column < self.columns):
            return True
        return self.layout[row][column] == Tile.WALL

    def is_walkable(self, x, y, radius=0):
        points = [
            (x, y),
            (x - radius, y),
            (x + radius, y),
            (x, y - radius),
            (x, y + radius),
        ]

        for point_x, point_y in points:
            row, column = self.world_to_grid(point_x, point_y)
            if self.is_wall(row, column):
                return False

        return True

