import random

from environment.tile import Tile


def generate_layout(rows=9, columns=15, rng=random):
    """Random "perfect" maze: exactly one path between any two floor cells.

    Depth-first search with backtracking: start at a cell, knock down the wall
    to a random unvisited neighbour two steps away, repeat; back up when stuck.
    rows and columns must be odd. Spawn is top-left, goal bottom-right.
    """
    if rows % 2 == 0 or columns % 2 == 0:
        raise ValueError("rows and columns must be odd")
    grid = [[Tile.WALL] * columns for _ in range(rows)]
    grid[1][1] = Tile.FLOOR
    stack = [(1, 1)]

    while stack:
        row, col = stack[-1]
        unvisited = [
            (row + dr, col + dc) for dr, dc in ((2, 0), (-2, 0), (0, 2), (0, -2))
            if 0 < row + dr < rows - 1 and 0 < col + dc < columns - 1
            and grid[row + dr][col + dc] == Tile.WALL
        ]
        if not unvisited:
            stack.pop()
            continue
        next_row, next_col = rng.choice(unvisited)
        grid[(row + next_row) // 2][(col + next_col) // 2] = Tile.FLOOR
        grid[next_row][next_col] = Tile.FLOOR
        stack.append((next_row, next_col))

    grid[1][1] = Tile.SPAWN
    grid[rows - 2][columns - 2] = Tile.GOAL
    return ["".join(row) for row in grid]
