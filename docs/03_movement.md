# 03 — Movement

## Purpose

Handles the physics of turning and translating an agent through the maze.
Owns the math; the agent simply delegates.

## Responsibilities

- **Owns**: Turn speed, angle modification (with normalization), forward/backward
  translation, collision queries via `maze.is_walkable()`.
- **Should never own**: The agent's state directly (it mutates via the passed
  reference), rendering, or decision-making.

## Key Algorithms

### Angle Normalization

After every turn:

```python
agent.angle %= math.tau   # keeps angle in [0, 2π)
```

Without this, the angle could grow unbounded (e.g., 5000 radians). Trigonometric
functions still work, but debugging becomes impossible.

### Forward / Backward Movement

```
next_x = x ± speed * cos(angle)
next_y = y ± speed * sin(angle)
```

The position only updates if `maze.is_walkable(next_x, next_y, radius)` returns
`True`. This is an instant rejection — no sliding along walls, no partial
movement. Simple and predictable.

## Design Decisions

- **Turn speed from config** — Defaulting to `config.TURN_SPEED` means we can
  tune rotation globally. Individual agents can override if needed.
- **No acceleration model** — Intentional. For neuroevolution, instant
  response (speed = constant) is simpler to learn. Acceleration can be added
  later as a research-level improvement.

## Future Improvements

- Wall sliding (project velocity along the wall normal).
- Acceleration / deceleration model.
- Different movement profiles per agent (fast but fragile vs. slow but sturdy).
