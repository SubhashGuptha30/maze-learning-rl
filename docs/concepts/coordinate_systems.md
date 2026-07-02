# Coordinate Systems

## Why This Matters

Every position, angle, and movement calculation in the project depends on
the coordinate system. A misunderstanding here causes invisible bugs:
agents that move backwards, sensors that point the wrong way, or collision
checks that miss entirely.

## Screen Coordinates (Pygame)

Pygame uses screen coordinates, which differ from mathematical coordinates:

```
(0, 0) ────────────► +X
  │
  │
  │
  ▼
  +Y
```

- **Origin (0, 0):** Top-left corner of the window.
- **+X:** Points right.
- **+Y:** Points down (not up — this is the critical difference).

This means:
- Moving "up" on screen requires *decreasing* Y.
- Moving "down" on screen requires *increasing* Y.
- `(100, 50)` is 100 pixels right, 50 pixels down from the top-left.

## Grid Coordinates

The maze uses a (row, column) system:

```
        column 0   column 1   column 2
row 0:    #           #           #
row 1:    #           S           .
row 2:    #           .           G
```

- **Row** increases downward (like Y).
- **Column** increases rightward (like X).
- `(row, column)` maps to `(y, x)` — note the swap.

### World-to-Grid Conversion

```
row    = floor(y / cell_size)
column = floor(x / cell_size)
```

The division by `cell_size` maps continuous world-space into discrete
grid-space. `floor` ensures we always round down to the cell the point
is inside.

### Grid-to-World Conversion

```
x = column × cell_size + cell_size / 2
y = row × cell_size + cell_size / 2
```

Adding `cell_size / 2` gives the center of the cell, not its top-left
corner.

## Angles (Radians)

We use radians, not degrees. One full rotation = 2π ≈ 6.283 radians.

```
         3π/2 (270°)
           │
           │
  π ───────●──────── 0 (0°)
(180°)     │
           │
         π/2 (90°)
```

**In screen coordinates (Y points down):**

- **0 radians** = right.
- **π/2 radians** = down (not up!).
- **π radians** = left.
- **3π/2 radians** = up.

This is the opposite of mathematical convention where π/2 points up.
It's a direct consequence of the Y-axis being flipped.

### Why Radians, Not Degrees?

`math.cos()` and `math.sin()` require radians. Using degrees would
require `math.radians()` conversion at every trigonometric call. Radians
eliminate this overhead and are the standard in physics and engineering.

### Angle Normalization

After any rotation, we apply:

```
angle = angle mod 2π
```

This keeps the angle in [0, 2π). Without normalization, repeated turns
would accumulate unbounded values (847.3 radians after many rotations),
making debugging impossible.

## Trigonometry in Movement

To move the agent forward by `speed` units in the direction it's facing:

```
next_x = x + speed × cos(angle)
next_y = y + speed × sin(angle)
```

- `cos(angle)` gives the X component of the direction.
- `sin(angle)` gives the Y component of the direction.

Because Y points down in screen coordinates, `sin(π/2) = 1` moves the
agent downward — which is correct for screen space.

## Common Pitfalls

1. **Confusing (row, col) with (x, y):** Rows correspond to Y, columns
   to X. The order is swapped. Every conversion must account for this.
2. **Assuming Y points up:** In math class, Y increases upward. In pygame,
   Y increases downward. Angles "rotate the wrong way" unless you remember
   this.
3. **Mixing degrees and radians:** `config.TURN_SPEED` is in radians.
   `math.degrees()` is used only for display in the debug overlay.
4. **Forgetting to normalize angles:** After many turns, an unnormalized
   angle becomes meaningless noise.
