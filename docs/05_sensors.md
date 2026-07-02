# 05 — Sensors

## 1. Purpose

The Sensor System is the only bridge between the physical environment and
intelligence. The neural network never sees the maze directly. It never
knows where walls are, how big the grid is, or where the goal is. It only
receives a small set of normalized numbers from the sensors.

This is exactly how real robots work. A self-driving car doesn't have
access to a bird's-eye view of the road. It has cameras, LIDAR, and radar
that produce readings. The AI interprets those readings.

Our sensors serve the same purpose: they reduce an entire 2D world into
five floating-point numbers that an artificial brain can learn from.

## 2. Responsibilities

**Owns:**
- Ray casting logic (projecting rays from the agent into the world).
- Storing hit points and normalized distances.
- Sensor configuration (angles, range, step size).
- Visualizing sensor rays on screen.

**Should Never Own:**
- Interpreting the readings (that's the brain's job).
- Modifying the agent's state (sensors are read-only observers).
- Maze structure or collision rules.
- Fitness calculation.

## 3. Theory

### Why Sensors Instead of Raw Grid Data?

The maze is a 9×16 grid = 144 cells. We could feed the entire grid into
the neural network as a 144-dimensional input. Why don't we?

**Input dimensionality** — A 144-input network needs vastly more weights
than a 5-input network. More weights means a larger genome, which means
slower evolution. The search space grows exponentially with input size.

**Position dependence** — Raw grid data is absolute. The agent would need
to learn its own position within the grid AND how to interpret wall
positions relative to itself. That's two problems in one.

**Generalization** — An agent trained on maze layout A would fail on layout
B because the raw grid pattern is completely different. Sensor readings are
layout-independent: "there's a wall 0.3 units ahead" means the same thing
in any maze.

**Biological inspiration** — Animals don't have GPS and satellite imagery
of their environment. They have eyes, whiskers, and antennae. Local
sensory information is sufficient for navigation.

### Why Five Sensors?

Five sensors at -90°, -45°, 0°, +45°, +90° give the agent:
- **Peripheral awareness** — Left and right sensors detect walls beside it.
- **Steering information** — Front-left and front-right sensors help with
  turning decisions.
- **Forward planning** — The front sensor detects what's directly ahead.

**Why not three?** Three sensors (left, front, right) lack diagonal
awareness. The agent can't distinguish "wall ahead-left" from "wall
directly left." It would frequently collide with diagonal obstacles.

**Why not ten?** More sensors means more inputs, which means more weights,
which means a larger genome. Each additional sensor adds computational
cost (more rays per frame) and learning cost (more weights to evolve).
Five was chosen experimentally as a sweet spot between awareness and
simplicity.

### Why Normalize to [0, 1]?

Neural networks work best when inputs are on a consistent scale. If one
sensor reads in [0, 200] pixels and another reads in [0, 1], the network
weights for the first sensor would need to be 200× smaller to have the
same effect. This creates an uneven learning landscape.

Normalization ensures every sensor reading is in [0, 1]:
- `0.0` → wall is touching the sensor origin.
- `1.0` → no wall detected within maximum range.

The network treats all sensors equally, and the genome search space is
uniform.

## 4. Data Flow

```
Maze (wall data)
      │
      ▼
Ray Casting (5 rays from agent's front surface)
      │
      ▼
Raw Distances (pixels)
      │
      ▼
Normalization (÷ max_range)
      │
      ▼
Sensor Readings [0.0 – 1.0]  ──►  Neural Network (future)
      │
      ▼
Hit Points (x, y)  ──►  Renderer (ray visualization)
```

## 5. Algorithm

### Ray Casting (Per Sensor)

```
FUNCTION cast_ray(agent, maze, relative_angle):
    ray_angle ← agent.angle + relative_angle

    origin ← agent.position + agent.radius × (cos(agent.angle), sin(agent.angle))
             ↑ front of body, not center

    distance ← 0
    hit ← None

    WHILE distance < max_range:
        point ← origin + distance × (cos(ray_angle), sin(ray_angle))
        (row, col) ← maze.world_to_grid(point)

        IF maze.is_wall(row, col):
            hit ← point
            BREAK

        distance ← distance + step_size

    IF hit is None:
        distance ← max_range
        hit ← origin + max_range × (cos(ray_angle), sin(ray_angle))

    RETURN (distance, hit)
```

### Sensor Update (All Sensors)

```
FUNCTION update(agent, maze):
    readings ← []
    hit_points ← []

    FOR EACH angle IN sensor_angles:
        (distance, hit) ← cast_ray(agent, maze, angle)
        readings.append(distance / max_range)
        hit_points.append(hit)

    Store readings and hit_points
```

### Ray Color (Visualization)

```
FUNCTION ray_color(normalized_distance):
    IF distance < 0.3:   RETURN RED      ← danger
    IF distance < 0.6:   RETURN ORANGE   ← caution
    ELSE:                 RETURN GREEN    ← safe
```

## 6. Sequence of Operations

```
Every Frame (per agent)
    │
    ├── Agent rotates (angle changes)
    │
    ├── agent.update(maze)
    │       │
    │       ▼
    │   SensorSystem.update(agent, maze)
    │       │
    │       ├── Compute sensor origin (front of body)
    │       │
    │       ├── For each of 5 angles:
    │       │       ├── Cast ray step-by-step
    │       │       ├── Check maze.is_wall() at each step
    │       │       ├── Record distance and hit point
    │       │       └── Normalize distance
    │       │
    │       └── Store all readings and hit points
    │
    └── SensorSystem.draw(screen, agent)
            └── Draw colored rays from origin to hit points
```

## 7. Design Decisions

### Sensor Origin at the Front, Not the Center

Rays originate from `(x + radius × cos(θ), y + radius × sin(θ))` — the
front surface of the agent's body, not its center.

**Why?** If rays start from the center and the agent is near a wall, the
ray might travel through the agent's own body before reaching the wall.
This produces artificially short readings. Starting from the front surface
eliminates this artifact.

**Trade-off:** Slightly more complex math (one extra trig computation per
update). Negligible cost.

### Step-Based Casting, Not Analytical

We advance each ray pixel-by-pixel (step_size=1) and check for walls at
each step.

**Why not analytical (DDA)?** Step-based casting is simpler to implement,
debug, and understand. DDA (Digital Differential Analyzer) jumps directly
to cell boundaries, which is faster but requires more complex setup.

For 5 rays × 200 max steps = 1000 iterations per agent per frame, the
step-based approach is fast enough. Worst case, with 500 agents, we'd
evaluate up to 500,000 grid lookups per frame (rays often terminate early)
— still manageable at O(1) per lookup.

### Distance-Based Ray Coloring

Rays change color based on normalized distance:
- RED (< 0.3) — danger, wall is close.
- ORANGE (0.3–0.6) — caution, wall is at medium range.
- GREEN (> 0.6) — safe, no nearby wall.

**Why?** When watching hundreds of agents train simultaneously, colored
rays give instant visual understanding of what each agent is sensing.
Yellow-only rays are indistinguishable at scale.

Ray visualization is purely a debugging aid and does not affect the
simulation. During headless training, it is skipped entirely.

## 8. Alternatives Considered

### DDA (Digital Differential Analyzer) Ray Casting

**How it works:** Instead of advancing pixel-by-pixel, compute exactly
where the ray crosses cell boundaries. Jump directly to those points.
**Advantages:** O(cells_crossed) instead of O(pixels). Significantly
faster for long-range rays.
**Disadvantages:** More complex implementation. Requires handling
horizontal and vertical cell crossings separately.
**Why deferred:** Step-based is fast enough for our scale. DDA becomes
worthwhile when max_range > 500 or agent count > 1000.

### Giving the Neural Network the Entire Grid

**Advantages:** Maximum information. The network could theoretically learn
optimal paths.
**Disadvantages:** 144 inputs instead of 5. Genome size explodes.
Position-dependent (doesn't generalize). See Theory section.
**Why rejected:** Sensors provide the right abstraction level for learning.

### Continuous-Angle Sensors (e.g., 360° Sweep)

**Advantages:** Full spatial awareness. No blind spots.
**Disadvantages:** Either very many sensors (high input dimensionality) or
low angular resolution. Both hurt learning.
**Why rejected:** Five well-placed sensors provide sufficient awareness
with minimal input dimensionality.

## 9. Complexity Analysis

| Operation | Algorithmic Complexity | Practical Cost (worst case) |
|-----------|----------------------|-----------------------------|
| Single ray cast | O(max_range / step) | ≤ 200 grid lookups |
| All sensors, one agent | O(5 × max_range) | ≤ 1,000 grid lookups |
| All sensors, N agents | O(N × 5 × max_range) | ≤ 1,000N grid lookups |

Worst case at 60 FPS with 500 agents: ~30 million grid lookups per second.
In practice, rays terminate early when they hit walls, so the actual cost
is substantially lower. Each lookup is a bounds check + array access —
well within modern CPU capacity.

## 10. Interaction With Other Modules

```
SensorSystem  ──reads──►  Maze.is_wall()
              ──reads──►  Agent.position, Agent.angle, Agent.radius
              ──returns──►  Brain (via get_readings())
              ──draws──►   Screen (via draw())
```

Sensors are pure observers. They read from the world and the agent, but
write to nothing external. Their output (readings) is consumed by
whatever intelligence system is active.

## 11. Future Improvements

- **DDA ray casting** — For performance at scale.
- **Sensor noise** — Add ±random offset to readings for robustness training.
  Real robots have noisy sensors; training with noise produces more robust
  neural networks.
- **Goal sensor** — A dedicated sensor pointing toward the goal, returning
  the distance. Provides direct fitness gradient information. Note: this
  intentionally leaks global task information into the agent's local
  perception, trading realism for faster convergence. It changes the
  learning problem from "explore to find the goal" to "navigate toward a
  known target."
- **Checkpoint sensor** — Detect nearby checkpoints.
- **Variable sensor count** — Allow the genome to evolve the number and
  angles of sensors (NEAT-style topology evolution).
