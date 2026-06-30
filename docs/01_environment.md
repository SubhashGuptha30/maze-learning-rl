# 01 — Environment (Maze)

## Purpose

The maze is the world the agent lives in. It defines walkable space, walls,
the spawn point, and the goal. Every other system queries the maze — sensors
ask "is this a wall?", movement asks "can I walk here?".

## Responsibilities

- **Owns**: The grid layout, cell size, wall/floor data, spawn/goal locations.
- **Should never own**: Agent logic, rendering order, or AI decisions.

## Key Algorithms

### World ↔ Grid Conversion

The maze stores data as a 2D string grid, but the agent lives in continuous
pixel space. Two helpers bridge the gap:

```
world_to_grid(x, y)  →  (row, column)   # pixel → grid
grid_to_world(row, column)  →  (x, y)   # grid → pixel center
```

### Walkability Check

`is_walkable(x, y, radius)` samples 5 points (center + 4 cardinal offsets by
`radius`) and returns `False` if any of them land on a wall. This gives
circle-based collision detection without expensive math.

## Design Decisions

- **String-based layout** was chosen for simplicity and readability. Each
  character maps to a `Tile` constant (`#`, `.`, `S`, `G`).
- **Cell size** is centralized in `config.py` so the entire world can be
  rescaled from one place.

## Future Improvements

- `MazeLoader` — Load layouts from `.txt` files for easy level swapping.
- Procedural maze generation (recursive backtracking or Prim's algorithm).
- Multiple goals and checkpoint tiles for richer fitness evaluation.
