# 04 — Collision

## Purpose

Collision prevents the agent from entering walls while allowing smooth
continuous movement through open space.

## Responsibilities

- Predict whether a proposed movement is valid.
- Reject invalid movement entirely (no partial moves).
- Treat positions outside the maze boundary as walls.

## Algorithm

1. Compute the proposed next position from the agent's speed and angle.
2. Sample five points around the agent's circular body (center + 4 cardinal).
3. Convert each world-space point to grid-space via `world_to_grid()`.
4. If any point lands inside a wall cell, reject the entire movement.
5. Otherwise, update the agent's position.

## Design Decisions

- **Predictive collision** — We check the *next* position before moving, not
  after. The agent never enters an invalid state. No tunneling, no correction.
- **Five-point circle approximation** — Sampling center + 4 cardinal offsets
  is fast and sufficient at our scale (`radius=10`, `cell_size=40`).
- **Reject, not correct** — When blocked, the agent stays put. No wall
  sliding, no push-back vectors. The neural network receives clear feedback:
  "this direction is blocked."
- **Maze owns collision** — The maze owns the world data, so it answers
  collision queries. Movement asks; the maze decides.

## Future Improvements

- Eight-point sampling (add diagonals for better corner accuracy).
- Circle-vs-rectangle intersection for pixel-perfect collision.
- Wall sliding (project rejected velocity onto the wall tangent).
- Continuous collision detection for very fast agents.
