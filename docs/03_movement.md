# 03 — Movement

## 1. Purpose

Movement translates intention into physical displacement. When a controller
says "move forward," the Movement system computes the resulting position,
checks whether it's valid, and updates the agent's state.

Without this module, agents could think but never act. Movement is the
bridge between intelligence and the physical world.

## 2. Responsibilities

**Owns:**
- Computing the next position from speed and angle.
- Turning the agent (modifying angle).
- Angle normalization (keeping angle in [0, 2π)).
- Querying the maze for walkability before committing movement.

**Should Never Own:**
- The agent's state directly (it mutates the agent passed as a parameter).
- Collision geometry (that belongs to the maze's `is_walkable`).
- Decision-making (that belongs to the controller/brain).
- Rendering.

## 3. Theory

### Why Instant Speed?

Our agents move at a constant speed with no acceleration, no momentum, and
no friction. When the controller says "forward," the agent moves exactly
`speed` pixels in the direction it's facing. When it says nothing, the
agent is perfectly still.

**Why?** For neuroevolution, simplicity in the physics model is an
advantage. The neural network's output maps directly to a result. If we
added acceleration, the network would need to learn:

1. How to accelerate.
2. How to decelerate.
3. How to compensate for momentum near walls.

That's three additional skills before it can even navigate. With instant
speed, the network only needs to learn direction and timing.

### Why Normalize Angles?

After every rotation, we apply:

```
angle ← angle mod 2π
```

Mathematically, `cos(θ)` and `cos(θ + 2πn)` are identical. So why bother?

1. **Debugging** — An angle of 4.71 radians (270°) is meaningful. An angle
   of 847.3 radians is meaningless noise.
2. **Neural network inputs** — If we ever feed the angle to the network
   (e.g., as a goal-direction sensor), unbounded values would break learning.
3. **Comparison** — Checking "is the agent facing north?" requires a
   predictable range.

### Why Movement is Separate from Agent

The agent is state. Movement is physics. They change for different reasons.

If we want ice physics (reduced friction), or tank controls (turn in place),
or acceleration-based movement, we swap the Movement object. The agent
doesn't know or care.

## 4. Data Flow

```
Controller Command ("move forward")
        │
        ▼
Movement.move_forward(agent, maze)
        │
        ├── Compute next position
        │     next_x = x + speed × cos(angle)
        │     next_y = y + speed × sin(angle)
        │
        ├── Query: maze.is_walkable(next_x, next_y, radius)?
        │         │
        │    ┌────┴────┐
        │    Yes       No
        │    │         │
        │    ▼         ▼
        │  Update    Reject
        │  position  (stay put)
        │
        ▼
Agent state updated (or not)
```

## 5. Algorithm

### Turn

```
FUNCTION turn_left(agent):
    agent.angle ← agent.angle - turn_speed
    agent.angle ← agent.angle mod 2π

FUNCTION turn_right(agent):
    agent.angle ← agent.angle + turn_speed
    agent.angle ← agent.angle mod 2π
```

### Move Forward

```
FUNCTION move_forward(agent, maze):
    next_x ← agent.x + agent.speed × cos(agent.angle)
    next_y ← agent.y + agent.speed × sin(agent.angle)

    IF maze.is_walkable(next_x, next_y, agent.radius):
        agent.x ← next_x
        agent.y ← next_y
```

### Move Backward

```
FUNCTION move_backward(agent, maze):
    next_x ← agent.x - agent.speed × cos(agent.angle)
    next_y ← agent.y - agent.speed × sin(agent.angle)

    IF maze.is_walkable(next_x, next_y, agent.radius):
        agent.x ← next_x
        agent.y ← next_y
```

## 6. Sequence of Operations

```
Every Frame (per agent)
    │
    ├── Controller decides action
    │
    ├── If turning:
    │       ├── Modify angle
    │       └── Normalize angle (mod 2π)
    │
    ├── If moving:
    │       ├── Compute proposed position
    │       ├── Query maze.is_walkable()
    │       └── Accept or reject
    │
    └── (Agent state is now final for this frame)
```

## 7. Design Decisions

### Predictive Collision (Check Before Move)

We check the destination BEFORE moving. The agent never occupies an
invalid position.

**Why not corrective?** Corrective collision (move first, then fix) requires
computing push-back vectors, handling corner cases where the agent is pushed
into another wall, and resolving cascading corrections. For AI training,
this complexity adds nothing. The neural network doesn't benefit from wall
sliding — it benefits from clear, deterministic feedback.

### No Acceleration Model

Speed is constant and instantaneous.

**Why not acceleration?** Three reasons:
1. **Learning complexity** — The network must learn acceleration curves in
   addition to navigation. This dramatically increases training time.
2. **Momentum near walls** — With momentum, the agent can't stop instantly
   before a wall. It must learn braking distance, which varies with speed.
3. **Determinism** — Given the same physical state and inputs, movement is
   deterministic. No hidden state (velocity) complicates the mapping
   from sensors to actions.

### Turn Speed from Config

The default turn speed is defined in `config.py` but can be overridden
per-agent.

**Why?** Global tuning. If agents turn too slowly, they can't navigate
tight corridors. Too fast, and control becomes erratic. One config change
adjusts the entire population.

## 8. Alternatives Considered

### Velocity-Based Movement (Physics Simulation)

```
velocity += acceleration × dt
position += velocity × dt
velocity *= friction
```

**Advantages:** More realistic. Smooth acceleration and deceleration.
**Disadvantages:** Hidden state (velocity) makes neural network training
harder. The network must learn when to brake, not just where to go.
**Why rejected:** Unnecessary complexity for a learning environment.

### Grid-Based Movement (Discrete Steps)

Move one cell at a time, like a chessboard.

**Advantages:** Trivially simple. No collision edge cases.
**Disadvantages:** Unnatural. Agents teleport between cells. Poor visual
feedback. The neural network can't learn fine-grained control.
**Why rejected:** We want continuous movement for realistic sensor readings
and smooth visual feedback.

## 9. Complexity Analysis

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| `turn_left()` / `turn_right()` | O(1) | One subtraction + modulo |
| `move_forward()` / `move_backward()` | O(1) | One trig pair + `is_walkable()` (5 lookups) |

Per agent, per frame: at most O(1) for movement. With 500 agents, total
movement cost is O(500) = O(n), linear in population size.

## 10. Interaction With Other Modules

```
Controller  ──commands──►  Movement
                             │
                             ├──  reads   ──►  Agent (angle, speed, position)
                             ├──  writes  ──►  Agent (angle, x, y)
                             └──  queries ──►  Maze.is_walkable()
```

Movement is the only module that **writes** to the agent's position and
angle. This makes it easy to trace where state changes originate.

## 11. Future Improvements

- **Wall sliding** — Project rejected velocity onto the wall tangent.
- **Acceleration model** — Optional, for more realistic simulations.
- **Variable speed** — Different agents move at different speeds (evolved).
- **Turn-and-move simultaneously** — Currently sequential; could be combined
  for smoother arcs.
