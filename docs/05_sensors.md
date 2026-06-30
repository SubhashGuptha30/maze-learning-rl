# 05 — Sensors

## Purpose

The sensor system gives the agent "eyes." It casts rays outward from the
agent's front surface and returns normalized distances to the nearest walls.
These readings will become the input vector for the neural network.

## Responsibilities

- **Owns**: Ray angles, max range, step size, raycasting logic, hit-point
  storage, normalized readings.
- **Should never own**: What to do with the readings (that's the brain's job),
  agent position (it reads but doesn't modify), or maze structure.

## Key Algorithms

### Raycasting (Step-Based)

For each sensor angle:

```
origin = agent_front (x + radius·cos(θ), y + radius·sin(θ))

for distance in [0, step, 2·step, ...]:
    point = origin + distance · (cos(ray_angle), sin(ray_angle))
    if maze.is_wall(point):
        return distance
return max_range
```

**Trade-off**: Step-based raycasting is O(max_range / step). For `max_range=200`
and `step=1`, that's at most 200 iterations per ray × 5 rays = 1000 iterations
per frame. Fast enough for real-time, but a DDA algorithm would be faster at
scale.

### Sensor Origin

Rays originate from the **front** of the agent's body, not the center. This
prevents false readings when the center is near a wall but the body isn't
actually touching it.

### Normalization

Each distance is divided by `max_range`, producing a value in `[0.0, 1.0]`:
- `0.0` → wall is touching the sensor origin
- `1.0` → no wall detected within range

This normalization is critical for neural network input — it ensures all
inputs are on the same scale regardless of max_range.

## Design Decisions

- **5 sensors at fixed angles** — Left (−90°), Front-Left (−45°), Front (0°),
  Front-Right (+45°), Right (+90°). This gives the neural network enough
  spatial awareness without excessive input dimensionality.
- **Configurable via config.py** — Angles, range, and step size are all
  externalized for easy experimentation.

## Future Improvements

- DDA (Digital Differential Analyzer) raycasting for O(cells) instead of O(pixels).
- Sensor noise (±small random offset) for robustness training.
- Goal sensor — a dedicated ray pointing toward the goal, returning distance.
- Checkpoint sensor — detect nearby checkpoints for fitness guidance.
