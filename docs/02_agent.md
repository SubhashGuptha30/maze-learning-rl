# 02 — Agent

## Purpose

The Agent is the entity that exists inside the maze. It holds physical state
(position, angle, radius, speed) and delegates behavior to its subsystems
(Movement, SensorSystem). It is deliberately "dumb" — it doesn't decide
anything on its own.

## Responsibilities

- **Owns**: Position (`x`, `y`), heading (`angle`), size (`radius`), alive
  status, color, and references to its Movement and SensorSystem.
- **Should never own**: Decision-making logic, rendering order, or maze data.

## Key Interface

| Property / Method      | Description                                |
|------------------------|--------------------------------------------|
| `position`             | Returns `(x, y)` tuple (property)          |
| `turn_left()`          | Delegates to `movement.turn_left(self)`    |
| `turn_right()`         | Delegates to `movement.turn_right(self)`   |
| `move_forward(maze)`   | Delegates to `movement.move_forward(...)`  |
| `move_backward(maze)`  | Delegates to `movement.move_backward(...)` |
| `draw(screen)`         | Renders the agent circle + heading line    |

## Design Decisions

- **Delegation pattern** — The agent doesn't contain movement math or sensor
  logic. This means we can swap Movement implementations (e.g., ice physics,
  acceleration-based) without touching the Agent class.
- **Default parameters from config** — `radius`, `speed`, and `color` all
  default to values from `config.py`, but can be overridden per-agent for
  diversity in a population.

## Future Improvements

- Fitness tracking (`agent.fitness`).
- Brain reference (`agent.brain`) — either an `InputController` or a
  `NeuralNetwork`.
- Genome reference for neuroevolution.
