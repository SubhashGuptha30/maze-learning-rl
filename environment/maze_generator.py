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


def generate_track(rows=9, columns=16, rng=random):
    """Random closed-loop race track, one cell wide, with no dead ends.

    The loop is the outline of a wobbly band: a top edge and a bottom edge that
    each random-walk up and down from column to column, joined at both ends.
    A wall cell between S and G acts as a finish line: the only way from S to
    G is a full lap, so "distance to G" means "how much of the lap is left".
    """
    left, right = 1, columns - 2
    top = [1] * columns
    bottom = [rows - 2] * columns
    for c in range(left + 1, right + 1):
        # Top edge stays flat on row 1 for the first columns: a straight, single-width
        # start/finish, so nobody can drive around the finish-line wall
        if c > left + 4:
            top[c] = min(max(top[c - 1] + rng.choice((-1, 0, 0, 1)), 1), rows // 2 - 1)
        bottom[c] = max(min(bottom[c - 1] + rng.choice((-1, 0, 0, 1)), rows - 2), rows // 2 + 1)

    grid = [[Tile.WALL] * columns for _ in range(rows)]

    def carve_column(c, r1, r2):
        for r in range(min(r1, r2), max(r1, r2) + 1):
            grid[r][c] = Tile.FLOOR

    for c in range(left, right + 1):
        carve_column(c, top[c], top[c - 1] if c > left else top[c])        # top edge, with steps
        carve_column(c, bottom[c], bottom[c - 1] if c > left else bottom[c])  # bottom edge, with steps
    carve_column(left, top[left], bottom[left])      # left side
    carve_column(right, top[right], bottom[right])   # right side

    # Start on the top edge heading right (agents spawn facing east); finish line just behind it
    grid[1][left + 1] = Tile.GOAL
    grid[1][left + 2] = Tile.WALL
    grid[1][left + 3] = Tile.SPAWN
    return ["".join(r) for r in grid]
