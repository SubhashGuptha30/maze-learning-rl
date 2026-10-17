# 02 — Agent

## 1. Purpose

The Agent is the entity that exists inside the world. It is the subject of
the entire project — everything else exists to serve, observe, or train it.

But the agent itself contains no decision-making logic. It holds physical
state (where it is, which way it faces, how fast it moves) and delegates
all behavior to subsystems. It doesn't decide how to move — that's the
controller's job. It doesn't sense the world — that's the sensor system's
job. It doesn't know about fitness — that's the evaluator's job.

The agent is a vessel. Intelligence flows through it, not from it.

## 2. Responsibilities

**Owns:**
- Physical state: position (x, y), heading (angle), size (radius), speed.
- Alive status and visual color.
- References to its Movement and SensorSystem subsystems.
- Drawing itself on screen.

**Should Never Own:**
- Decision-making logic (belongs to the controller/brain).
- Maze data or collision rules (belongs to the environment).
- Fitness scoring (belongs to a future FitnessEvaluator).
- Neural network weights (belongs to a future Genome).

## 3. Theory

### Entity vs. Intelligence

In many beginner projects, the "agent" class becomes a god object. It
holds the neural network, calculates fitness, handles input, manages
sensors, and draws itself. Everything goes into one class because
"the agent does everything."

This is a design anti-pattern. When one class owns everything, changing
one concern (e.g., how fitness is calculated) risks breaking unrelated
concerns (e.g., how the agent draws itself).

Our agent follows the **delegation pattern**: it owns state, but delegates
behavior. This is inspired by the component-based architecture used in
many game engines, where an entity holds references to components
(Movement, Sensors, Brain) that provide behavior.

### Why Separate Position from Behavior?

Consider two agents with identical neural networks but different starting
positions. They should behave differently because their sensors read
different values. The agent's state (position) creates the context; the
brain interprets that context.

If position and intelligence were tangled in one class, creating a
population of agents with shared brains but independent positions would
require ugly workarounds. Separation makes it trivial.

## 4. Data Flow

```
Controller / Brain
        │
        │  calls turn_left(), move_forward(), etc.
        ▼
      Agent  ──delegates──►  Movement  ──queries──►  Maze
        │
        │  agent.update(maze)
        ▼
   SensorSystem  ──queries──►  Maze
        │
        ▼
   Normalized Readings [0.0 – 1.0]
        │
        ▼
   Neural Network
```

## 5. Algorithm

### Update Cycle

```
FUNCTION agent.update(maze):
    sensors.update(self, maze)
    — Future: fitness tracking
    — Future: internal timers
```

Note: the brain (controller) is NOT called inside `agent.update()`. It is
called externally by the main loop via `controller.update(agent, maze)`.
This keeps the controller as a swappable, external component rather than
an internal dependency. See [06_brain.md](06_brain.md) for the rationale.

### Drawing

```
FUNCTION agent.draw(screen):
    IF NOT alive:
        RETURN

    Draw filled circle at (x, y) with radius
    Compute tip = (x, y) + (radius + heading_length) × (cos θ, sin θ)
    Draw line from center to tip  ← heading indicator
```

## 6. Sequence of Operations

```
Every Frame
    │
    ├── Controller calls agent.turn_left() / move_forward() / etc.
    │       └── Agent delegates to Movement
    │
    ├── agent.update(maze)
    │       └── SensorSystem.update(agent, maze)
    │           └── Cast 5 rays, store normalized readings
    │
    └── agent.draw(screen)
            └── Circle + heading line
```

## 7. Design Decisions

### Delegation Over Inheritance

We could have created `KeyboardAgent`, `NeuralNetworkAgent`, `RuleBasedAgent`
as subclasses. But then switching brains at runtime requires replacing the
entire agent object. With delegation, we swap one component.

**Trade-off:** Slightly more indirection (agent.movement.move_forward vs.
agent.move_forward). But the flexibility gain is enormous.

### Default Parameters from Config

The constructor defaults (`radius=config.AGENT_RADIUS`,
`speed=config.AGENT_SPEED`) allow creating a "standard" agent with zero
arguments beyond ID and position. But every parameter can be overridden
per-agent for population diversity.

**Why?** In evolution, mutating physical parameters (speed, radius) alongside
neural weights creates a richer search space. Defaults from config give us
a baseline; overrides give us variation.

### Position as a Property

`agent.position` returns `(x, y)` as a tuple. Other systems use this
instead of reaching into `agent.x` and `agent.y` directly.

**Why?** Encapsulation. If we later change the internal representation
(e.g., to a Vector2 class), only the property needs updating.

## 8. Alternatives Considered

### God Object (Agent Does Everything)

**Advantages:** Simple to understand initially. Everything in one file.
**Disadvantages:** Becomes unmaintainable. Changing sensors breaks movement.
Adding evolution means editing the agent class. Testing requires the
entire system.
**Why rejected:** Violates single responsibility. Doesn't scale to
populations of hundreds of agents.

### Pure Entity-Component-System (ECS)

**Advantages:** Maximum flexibility. Industry standard in game engines.
**Disadvantages:** Significant boilerplate. Requires a component registry,
system scheduler, and message passing. Overkill for our scope.
**Why rejected:** Our component-based composition gives us 80% of the
benefit with 20% of the complexity.

## 9. Complexity Analysis

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| `update(maze)` | O(sensors) | Delegates to SensorSystem (see 05) |
| `draw(screen)` | O(1) | One circle + one line |
| `move_forward()` | O(1) | Delegates to Movement (see 03) |
| Property access | O(1) | Direct attribute lookup |

The agent itself adds negligible overhead. Cost lives in the subsystems.

## 10. Interaction With Other Modules

```
Controller  ──commands──►  Agent  ──delegates──►  Movement
                             │
                             ├──  owns  ──►  SensorSystem
                             │
Renderer    ──calls────►  Agent.draw()
                             │
main.py     ◄──reads────  Agent.position, Agent.alive
(fitness)
```

The agent is the central hub. Every system interacts with it, but no
system depends on the agent's internals — only its public interface.

## 11. Future Improvements

- **Genome reference** — For neuroevolution, each agent carries its genome.
- **Fitness tracking** — `agent.fitness` accumulated over a generation.
- **Termination conditions** — Timeout, blocked movement limit, inactivity
  detection.
- **Visual differentiation** — Color agents by fitness, species, or alive
  status during population training.
