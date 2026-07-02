# Raycasting

## What Is Raycasting?

Raycasting is a technique for determining what a ray (a line extending from
a point in a direction) hits in a world. It answers the question: "If I
look in this direction, what's the first thing I see, and how far away
is it?"

## Where Is It Used?

### Video Games

The original Wolfenstein 3D (1992) used raycasting to render an entire 3D
scene from a 2D map. For each vertical column of the screen, a ray was
cast from the player's position. The distance to the nearest wall
determined the height of the column drawn on screen — closer walls appear
taller.

This technique gave the illusion of 3D without actual 3D geometry.

### Robotics

LIDAR (Light Detection And Ranging) is physical raycasting. A laser beam
is emitted, bounces off surfaces, and returns. The time delay gives the
distance. Self-driving cars use hundreds of LIDAR rays per second to build
a 3D point cloud of their surroundings.

Our sensor system is a simplified 2D LIDAR simulation.

### Physics Engines

Raycasting is used for:
- **Line of sight** — Can character A see character B?
- **Projectile paths** — Where does a bullet hit?
- **Ground detection** — Is the character standing on a surface?

## How We Use It

We cast 5 rays from the agent's front surface at fixed angles. Each ray
advances step-by-step through the grid until it hits a wall or reaches
maximum range. The distance is then normalized to [0, 1] for neural
network input.

```
Agent facing right, 5 rays:

                         ╱ -90° (left)
                       ╱
                     ╱ -45° (front-left)
    ● ─────────────────── 0° (front)
                     ╲
                       ╲ +45° (front-right)
                         ╲ +90° (right)
```

## Methods

### Step-Based (What We Use)

Advance the ray by a fixed increment (e.g., 1 pixel) and check for
collisions at each step.

**Complexity:** O(max_range / step_size)
**Pros:** Simple to implement. Works with any grid representation.
**Cons:** Slower for long ranges. May miss sub-pixel features.

### DDA (Digital Differential Analyzer)

Compute the exact positions where the ray crosses cell boundaries. Jump
directly between cell crossings instead of stepping pixel-by-pixel.

**Complexity:** O(cells_crossed)
**Pros:** Much faster. Exact cell-boundary detection.
**Cons:** More complex implementation. Must handle horizontal and vertical
crossings separately.

### Analytical (Line-Segment Intersection)

Compute the mathematical intersection of the ray with every wall segment.

**Complexity:** O(wall_segments) per ray
**Pros:** Exact. Works with arbitrary polygon obstacles.
**Cons:** Requires storing wall segments explicitly. Slow for many walls.
Not necessary for grid-based worlds.

## Why Step-Based For Us

Our grid cells are 40×40 pixels. Our max range is 200 pixels. A single ray
crosses roughly 5–8 cells depending on angle. Step-based casting performs
at most 200 checks, each O(1). Even with 5 rays × 500 agents = 500,000
checks per frame, modern CPUs handle this comfortably.

DDA would reduce this to ~5–8 checks per ray × 5 rays × 500 agents =
roughly 12,500–20,000 checks. A significant improvement at extreme scale,
but unnecessary at our current scope.
