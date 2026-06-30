# 04 — Collision

## Purpose

Collision detection determines whether an agent can move to a given position.
Currently handled inline by `Maze.is_walkable()` and `Maze.is_wall()`.

## Responsibilities

- **Owns**: The logic for determining if a circle (agent) overlaps with walls.
- **Should never own**: Movement decisions (that's Movement's job) or rendering.

## Key Algorithms

### 5-Point Circle Approximation

Instead of true circle-vs-rectangle intersection, we sample 5 points:

```
        (x, y-r)
           │
(x-r, y) ─ ● ─ (x+r, y)
           │
        (x, y+r)
```

If any of these 5 points lands in a wall cell, the position is rejected.

**Trade-off**: This is fast and simple but can miss corners. For our cell
sizes and agent radii, it works well. A true circle-AABB test would be needed
only if agents become large relative to cells.

### Out-of-Bounds = Wall

`is_wall()` returns `True` for any `(row, column)` outside the grid bounds.
This means agents cannot escape the maze even if there's no border wall drawn.

## Design Decisions

- **No separate collision.py yet** — The logic is simple enough to live inside
  `maze.py`. The `collision.py` file is reserved for when we need SAT, swept
  collision, or agent-vs-agent detection.

## Future Improvements

- True circle-AABB intersection for pixel-perfect collision.
- Wall sliding (project rejected movement onto the wall tangent).
- Agent-vs-agent collision (needed once population > 1 shares the maze).
