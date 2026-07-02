# Floating Point and Trigonometry

## Why Floating-Point Positions?

The agent's position could be stored as integers (pixel coordinates) or
floating-point numbers. We chose floats.

### Why Not Integers?

Integer positions snap to whole pixels. An agent at `(100, 200)` moving
at speed 2 would go to `(102, 200)`. But what if the angle requires
moving 1.7 pixels in X and 1.1 pixels in Y?

With integers, we'd round: `(102, 201)`. This introduces directional
bias — over many frames, the rounding errors accumulate and the agent
drifts from its intended path. Diagonal movement becomes especially
inaccurate.

With floats: `(101.7, 201.1)`. The position is exact. We only round to
integers at the very end, when drawing to screen. The physics stay clean;
the rendering is approximate. This is standard practice in game
development.

### Where Rounding Happens

```
Physics:   agent.x = 182.37, agent.y = 133.91   ← float (exact)
Rendering: draw circle at (182, 134)             ← int (rounded for display)
Grid:      world_to_grid(182.37, 133.91) = (3, 4) ← int (floored)
```

Rounding only happens at the boundary between continuous physics and
discrete systems (rendering, grid lookup). The core simulation always
uses floats.

## Why Radians?

### The Mathematical Reason

Python's `math.cos()` and `math.sin()` accept radians. Using degrees
would require conversion at every trigonometric call:

```python
# With degrees (wasteful):
x += speed * math.cos(math.radians(angle_degrees))

# With radians (direct):
x += speed * math.cos(angle_radians)
```

Radians eliminate this conversion overhead.

### The Conceptual Reason

Radians are the natural unit for angles in mathematics and physics:
- A full circle = 2π radians.
- Arc length = radius × angle (only in radians).
- Derivatives of sin/cos are simple (only in radians).

Degrees are a human convenience (360° = 2π). They add conversion noise
to every calculation.

## Why cos and sin?

### Decomposing Direction into Components

An agent facing angle θ wants to move `speed` units in that direction.
But the screen has two independent axes (X and Y). We need to decompose
the diagonal movement into horizontal and vertical components.

```
                    ╱ speed
                  ╱
                ╱ θ
    ────────────
    speed × cos(θ)    ← horizontal component
         │
         │ speed × sin(θ)    ← vertical component
```

- `cos(θ)` gives the fraction of movement along the X axis.
- `sin(θ)` gives the fraction of movement along the Y axis.

Together: `(speed × cos(θ), speed × sin(θ))` is a vector pointing in
direction θ with length `speed`.

### Why This Works for Any Angle

| Angle (radians) | cos(θ) | sin(θ) | Direction |
|-----------------|--------|--------|-----------|
| 0 | 1 | 0 | Right |
| π/2 | 0 | 1 | Down (screen Y) |
| π | -1 | 0 | Left |
| 3π/2 | 0 | -1 | Up (screen Y) |
| π/4 | 0.707 | 0.707 | Diagonal (down-right) |

At any angle, cos and sin automatically produce the correct X and Y
components. No special cases needed for "moving diagonally" or "moving
backwards."

## Floating-Point Precision

### Does It Matter?

A 64-bit float (`float` in Python) has about 15-17 significant decimal
digits. For positions in a 640×360 window, we need at most 3 digits of
integer precision and perhaps 2-3 decimal places for smooth movement.
We have precision to spare.

### When It Could Matter

If the simulation ran for millions of frames with very small movements,
floating-point accumulation errors could theoretically cause drift. In
practice, our simulation resets agents every generation (every few
thousand frames), so accumulated error never becomes significant.

## In Our Project

- **Position:** `float` (agent.x, agent.y). Rounded to `int` only for
  rendering.
- **Angle:** `float` in radians. Normalized to [0, 2π) after every
  rotation.
- **Speed:** `float`. Allows fine-grained speed differences between agents.
- **Sensor distances:** `float`. Normalized to [0.0, 1.0] for neural
  network input.
