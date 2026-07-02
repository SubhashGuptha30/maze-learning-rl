# The Simulation Loop

## Why Games Use a Loop

Every interactive simulation — games, robotics simulators, physics engines
— runs a continuous loop. The loop repeatedly:

1. Reads input (keyboard, sensors, or AI decisions).
2. Updates the world state (physics, collisions, AI).
3. Renders the result (draws to screen).

Without a loop, the program would execute once and exit. The loop is what
makes the simulation *live* — it creates the illusion of continuous time
from discrete steps.

## The Structure of Our Loop

```
while running:
    events()          ← check for quit
    controller.update(agent, maze)   ← input/AI
    agent.update(maze)               ← physics + sensors
    draw()                           ← render
    clock.tick(FPS)                  ← timing
```

Each iteration of this loop is called a **frame**. At 60 FPS, the loop
executes 60 times per second, and the entire world is rebuilt from scratch
on screen 60 times every second.

## Why Updates Occur Before Rendering

The update step modifies state. The render step reads state and draws it.
If we rendered first, we'd draw the *previous* frame's state. The screen
would always be one frame behind reality.

By updating first, the screen shows the most current state:

```
Frame N:
  1. Controller says "move forward"
  2. Agent moves to (182.4, 133.7)
  3. Sensors cast rays from new position
  4. Screen draws agent at (182.4, 133.7)  ← matches reality
```

## Fixed Timestep vs. Variable Timestep

### Fixed Timestep (What We Use)

`clock.tick(60)` pauses the loop until 1/60th of a second has elapsed.
Every frame represents the same amount of real time.

**Advantages:**
- **Deterministic.** The same inputs produce the same outputs every time.
  This is critical for AI training: reproducibility lets us compare
  genomes fairly.
- **Stable physics.** Movement is `speed` pixels per frame. If frames are
  always 1/60th of a second, movement is consistent.
- **Simple.** No `dt` parameter needed. Speed is implicitly "per frame."

**Disadvantage:**
- If the computer can't maintain 60 FPS (e.g., too many agents), the
  simulation slows down. Real time passes, but fewer frames execute.

### Variable Timestep (Common in Games)

```
dt = clock.tick() / 1000.0   ← seconds since last frame
x += speed * dt              ← distance depends on elapsed time
```

**Advantages:**
- Simulation runs at real-time speed regardless of frame rate.
- Smooth on both fast and slow hardware.

**Disadvantages:**
- **Non-deterministic.** Different frame rates produce slightly different
  physics results (floating-point arithmetic is not associative across
  different `dt` values).
- **Harder to debug.** The same input can produce different outputs
  depending on system load.
- **Requires `dt` everywhere.** Every movement, timer, and physics
  calculation must multiply by `dt`.

### Why Fixed for AI Training

In neuroevolution, we compare agents' fitness across generations. If
frame timing varies, the same genome might score differently on different
runs. Fixed timestep eliminates this variable.

We also don't care about "real time" during training. If the simulation
runs at 10× speed (no rendering, no `clock.tick`), that's desirable. We
want consistent frames, not consistent wall-clock time.

## Why `clock.tick(FPS)` Matters

Without `clock.tick()`, the loop runs as fast as the CPU allows — possibly
thousands of frames per second. This:

1. Wastes CPU resources (100% utilization for no benefit during human play).
2. Makes the simulation too fast to observe visually.
3. Doesn't affect AI training (we could remove it during headless runs).

`clock.tick(60)` throttles the loop to 60 FPS, giving a consistent 16ms
per frame. The debug overlay shows the actual FPS for monitoring.

## Determinism and Reproducibility

A deterministic simulation means: given the same initial conditions and
inputs, the simulation produces exactly the same results every time.

Our simulation achieves this through:
1. **Fixed timestep** — Same time per frame, always.
2. **No randomness in physics** — Movement and collision are purely
   mathematical.
3. **Predictable input** — Neural networks are deterministic functions
   (same weights + same inputs = same outputs).

The only source of non-determinism is the initial population (random
genomes). Once genomes are fixed, every agent's lifetime is reproducible.
This is invaluable for debugging: "agent #47 crashed at frame 312" will
happen identically every time you replay it.

## The Frame as a Unit of Time

In our simulation, the frame is the fundamental time unit — not seconds,
not milliseconds. Everything is measured in frames:

- **Speed:** 2.5 pixels *per frame*.
- **Lifetime:** 1000 *frames* per generation.
- **Sensor readings:** Updated once *per frame*.

This is simpler than seconds-based timing and perfectly adequate for AI
training. We only care about frames when comparing agents: did agent A
survive more frames than agent B?

## Future: Headless Mode

During AI training, rendering is the bottleneck. Drawing 500 agents with
sensors at 60 FPS is expensive. Removing the rendering step and the
`clock.tick()` call lets the simulation run thousands of frames per
second — dramatically accelerating evolution.

```
Headless loop:
    controller.update(agent, maze)
    agent.update(maze)
    — no draw()
    — no clock.tick()
```

The simulation produces identical results whether rendered or headless,
because the physics are frame-based and independent of rendering.
