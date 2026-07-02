# 04 — Collision Design

## 1. Purpose

This document explains the *design* of collision in the simulator — the
choices we made, the trade-offs we accepted, and why collision works the
way it does.

The collision *implementation* (algorithms, pseudocode, data flow) lives
in [01_environment.md](01_environment.md), because collision queries are
owned by the Maze class. This document focuses on the *reasoning* behind
those implementation choices.

## 2. Responsibilities

**The Maze collision system owns:**
- Determining if a world-space position is occupied by a wall.
- Approximating a circular body with sample points.
- Treating out-of-bounds positions as walls.

Collision logic lives inside `Maze` (via `is_wall`, `is_walkable`),
not in a separate collision class. See Design Decision #1 below.

**Should Never Own:**
- What to do when a collision is detected (that's Movement's decision).
- Computing the next position (that's Movement's job).
- Rendering collision feedback.
- Agent state.

## 3. The Two Schools of Collision

Every collision system in every simulation must answer two questions:

1. **Detection** — Is this position invalid?
2. **Response** — What do we do about it?

These are fundamentally different concerns, and they lead to two very
different design philosophies.

### Predictive (What We Use)

Check the destination *before* moving. If it's invalid, reject the move.
The agent never occupies a bad state.

```
Proposed position → Valid? → Yes → Move
                           → No  → Stay put
```

**Properties:**
- The agent's state is *always* valid. Every frame, every agent.
- No correction math. No push-back vectors. No cascading resolutions.
- Deterministic feedback: "this direction is blocked" = movement rejected.
  Clean, unambiguous signal for the neural network.

### Corrective (What We Don't Use)

Move first, then detect overlap, then push the agent back to a valid
position.

```
Move to proposed position → Overlap detected → Compute penetration
  → Compute contact normal → Push agent back → Check for new overlaps
  → Resolve cascading collisions
```

**Properties:**
- Requires penetration depth, contact normals, and resolution vectors.
- Edge case: being pushed out of one wall and into another.
- The agent temporarily exists in an invalid state (inside a wall) and
  must be corrected. This makes the simulation harder to reason about.

### Why We Chose Predictive

For AI training, the agent needs clear feedback. Predictive collision
provides a binary signal: "I tried to move and it worked" or "I tried
to move and it didn't." There's no ambiguity, no partial movement, no
hidden physics the neural network must learn.

Corrective collision is standard in game engines because it enables wall
sliding (projecting rejected velocity along the wall tangent), which feels
natural for human players. But for AI training, wall sliding is
counterproductive — agents learn to press against walls instead of
avoiding them.

## 4. The Approximation Decision

### The Problem

Our agents are circles. The maze is a grid of rectangles. How do we check
if a circle overlaps a rectangle?

### True Circle-vs-AABB

The mathematically correct approach:
1. Find the closest point on the rectangle to the circle center.
2. Compute the distance from that point to the center.
3. If distance < radius, there's a collision.

This is accurate but requires closest-point geometry calculations against
each nearby wall cell (clamp center to rect, compute squared distance).
With multiple adjacent walls, we must check against each one.

### Our Choice: 5-Point Sampling

Instead of a true circle, we sample 5 points — center + 4 cardinal
directions:

```
             N
             │
     W ──── ● ──── E
             │
             S
```

If any point lands inside a wall cell, the position is rejected.

### When This Fails

When the agent approaches a wall corner at exactly 45°. The diagonal edge
of the circle might clip through because no sample point covers that spot:

```
     ┌──────┐
     │ WALL │
     └──────●──── The corner of the circle enters
              \   the wall, but no sample point
               \  detects it.
```

At our scale (radius=10, cell_size=40), this edge case is rare and
visually imperceptible. The circle's diagonal extent is only ~14 pixels,
well within the 40-pixel cell boundary for typical positions.

### Progression of Accuracy

| Points | Coverage | Cost | Notes |
|--------|----------|------|-------|
| 5 | Cardinal only | 5 lookups | What we use |
| 8 | Cardinal + diagonal | 8 lookups | Catches 45° clips |
| 16 | Every 22.5° | 16 lookups | Near pixel-perfect |
| True circle | Exact | Closest-point-on-rect per wall | Requires geometry math |

We chose 5 because the accuracy is sufficient for our agent/cell size
ratio, and the cost is minimal.

## 5. The Rejection Decision

When a collision is detected, the agent stays put. It doesn't slide,
bounce, or deflect.

### Why Not Wall Sliding?

Wall sliding projects the rejected movement vector onto the wall's
tangent, allowing the agent to glide along walls. This feels natural for
human play but creates a problem for AI training:

**Without sliding:** Agent pushes into a wall → agent stops → neural
network learns "this direction is blocked, try a different one."

**With sliding:** Agent pushes into a wall → agent slides along it →
neural network learns "pushing into walls is fine, I still make progress."

Sliding trains the network to *lean on* walls rather than *avoid* them.
Rejection trains the network to steer cleanly.

### Why Not Bouncing?

Bouncing (reflecting the velocity vector off the wall normal) adds hidden
physics. The neural network would need to learn not just "is there a wall?"
but also "what angle will I bounce at?" This dramatically increases the
complexity of the mapping from sensors to actions.

## 6. Boundary Treatment

Positions outside the grid are treated as walls. This means the maze is
implicitly surrounded by an infinite wall boundary.

**Why?** Safety. Even if the maze layout has no border walls, agents
cannot escape. It also simplifies sensor raycasting — rays that leave the
grid simply stop, rather than causing index-out-of-bounds errors.

## 7. Why Maze Owns Collision

The collision logic lives inside `Maze`, not in a separate module.

**Principle:** Data and the logic that queries it should live together.
Only the Maze knows where walls are. Extracting collision into a separate
class would require passing the grid layout as a parameter or creating a
tight coupling between Collision and Maze.

By keeping collision inside Maze, we get:
- No data duplication.
- A clean API: `maze.is_walkable(x, y, radius)`.
- One place to update if the world representation changes.

**When to extract:** If collision grows to include agent-vs-agent
detection, CCD (continuous collision detection), or multi-layer worlds,
a dedicated collision module would be justified. The reserved
`collision.py` file exists for this purpose.

## 8. Complexity

| Operation | Algorithmic Complexity | Practical Cost |
|-----------|----------------------|----------------|
| `is_wall()` | O(1) | 1 bounds check + 1 array lookup |
| `is_walkable()` | O(1) | 5 × `is_wall()` = 5 constant-time lookups |
| Per agent, per frame | O(1) | At most one walkability check per move |
| Population of N agents | O(N) | Linear in population size |

Collision adds negligible cost to the simulation.

## 9. No Continuous Collision Detection

We check only the destination, not the path between the current and
proposed position. A very fast agent could theoretically "tunnel" through
a thin wall.

**Why acceptable?** Our walls are 40px wide and agents move at 2.5px per
frame. Tunneling requires speed > wall_thickness, which is 16× our
current speed. If we later increase speed or decrease wall thickness, CCD
(checking along the movement vector) becomes necessary.

## 10. Future Evolution

- **8-point sampling** — Add diagonal sample points for better accuracy.
- **Circle-vs-AABB** — True geometric intersection for large agents.
- **Wall sliding** — Optional mode for human play or advanced training.
- **Continuous collision detection** — Path checking for high-speed agents.
- **Blocked movement events** — Emit events when movement is rejected so
  fitness can penalize wall-hugging behavior. (Note: in our predictive
  system, no actual collision occurs — movement is simply rejected.)
- **Agent-vs-agent collision** — Required when a population shares the maze.
