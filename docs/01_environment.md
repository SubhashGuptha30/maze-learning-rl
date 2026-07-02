# 01 — Environment

## 1. Purpose

The environment is the world the agent inhabits. Without it, there is nothing
to navigate, nothing to sense, and nothing to learn from.

Every intelligent system needs a world to act upon. In robotics, that world
is physical. In our simulator, it is a discrete grid that approximates a
physical space. The maze defines the rules of reality: where the agent can
exist, where it cannot, and where it should try to reach.

## 2. Responsibilities

**Owns:**
- The grid layout (walls, floors, spawn, goal).
- Cell size and world dimensions.
- Coordinate conversion between world-space and grid-space.
- Answering spatial queries: "Is this a wall?", "Can the agent stand here?",
  "Has the agent reached the goal?"

**Should Never Own:**
- Agent state, movement logic, or decision-making.
- Rendering order or visual presentation details.
- Fitness evaluation or AI-related concerns.

## 3. Theory

### Why a Grid?

A grid is the simplest spatial representation that supports collision and
pathfinding. Every cell is either traversable or not. There are no curves,
no floating-point boundaries, no polygon meshes.

The alternative — a continuous 2D space with polygon obstacles — would require
computational geometry (line-segment intersection, convex hull queries,
spatial partitioning). For an AI training environment where we need
thousands of fast evaluations per second, that complexity is unnecessary.

A grid gives us O(1) collision lookups. A naïve polygon implementation
requires checking many edges per query (though acceleration structures
like BSP trees or quadtrees can improve this significantly).

### Why Not Give the Neural Network the Entire Grid?

The grid is a 9×16 = 144-cell structure. We could flatten it into a 144-input
vector for the neural network. But this creates several problems:

1. **Scale dependence** — A larger maze means a larger input, which means a
   larger network, which means more weights, which means slower evolution.
2. **Spatial awareness** — The raw grid doesn't tell the agent "there's a
   wall 3 units ahead." It says "cell (4,7) is a wall." The agent would need
   to learn its own position within the grid AND the meaning of relative
   distances. That's vastly harder.
3. **Generalization** — An agent trained on one maze layout would fail on
   another because the input pattern is entirely different. Sensor-based
   input is layout-independent.

This is why we use sensors as an intermediary. The maze provides the ground
truth; sensors translate it into a format the neural network can learn from.

## 4. Data Flow

```
Maze Layout (strings)
      │
      ▼
find_special_tiles()  ──►  Spawn Position, Goal Position
      │
      ▼
world_to_grid(x, y)  ◄──  Agent Position (world-space)
      │
      ▼
is_wall(row, col)     ──►  Boolean (used by Movement, Sensors)
      │
      ▼
is_walkable(x, y, r)  ──►  Boolean (used by Movement)
      │
      ▼
reached_goal(agent)   ──►  Boolean (used by Fitness, future)
```

## 5. Algorithm

### Coordinate Conversion

```
FUNCTION world_to_grid(x, y):
    row    ← floor(y / cell_size)
    column ← floor(x / cell_size)
    RETURN (row, column)

FUNCTION grid_to_world(row, column):
    x ← column × cell_size + cell_size / 2
    y ← row × cell_size + cell_size / 2
    RETURN (x, y)
```

### Wall Query

```
FUNCTION is_wall(row, column):
    IF (row, column) is outside grid bounds:
        RETURN True      ← outside the maze = wall
    RETURN layout[row][column] == '#'
```

### Walkability Check (5-Point Circle Approximation)

```
FUNCTION is_walkable(x, y, radius):
    sample_points ← [
        (x, y),              ← center
        (x - radius, y),     ← left
        (x + radius, y),     ← right
        (x, y - radius),     ← top
        (x, y + radius),     ← bottom
    ]
    FOR EACH point IN sample_points:
        IF is_wall(world_to_grid(point)):
            RETURN False
    RETURN True
```

### Goal Detection

```
FUNCTION reached_goal(agent):
    distance ← euclidean(agent.position, goal.position)
    RETURN distance < GOAL_RADIUS
```

## 6. Sequence of Operations

```
Game Start
    │
    ▼
Maze.__init__()
    │
    ├── Parse layout strings
    ├── Calculate dimensions
    └── find_special_tiles()  ──►  Store spawn + goal positions
    │
    ▼
Every Frame
    │
    ├── Movement asks:  maze.is_walkable(next_x, next_y, radius)
    ├── Sensors ask:    maze.is_wall(row, column)
    ├── (Future) Fitness asks: maze.reached_goal(agent)
    └── Renderer calls: maze.draw(screen)
```

## 7. Design Decisions

### String-Based Layout

The maze is defined as a list of strings, where each character maps to a
tile type (`#` = wall, `.` = floor, `S` = spawn, `G` = goal).

**Why?** Readability. You can literally see the maze by looking at the source
code. No external editor, no binary format, no deserialization logic.

**Trade-off:** Not easily editable at runtime. But for our use case —
static training environments — this is perfectly acceptable.

### Cell Size as a Global Constant

Cell size is defined once in `config.py`. Every module that needs it
imports it from there.

**Why?** Changing the visual scale of the entire world requires editing
one number. If cell size were scattered across files, a mismatch between
the maze and the agent would cause invisible collision bugs.

### Out-of-Bounds = Wall

Instead of throwing an error when a query falls outside the grid, we return
`True` (it's a wall). This means the maze is implicitly surrounded by an
infinite wall boundary.

**Why?** Safety. Even if the maze layout has no border walls, agents cannot
escape. It also simplifies sensor raycasting — rays that leave the grid
simply stop, rather than causing index errors.

## 8. Alternatives Considered

### Continuous 2D Space with Polygon Obstacles

**Advantages:** Smooth curves, arbitrary shapes, more realistic.
**Disadvantages:** Requires computational geometry (line intersection,
point-in-polygon). Collision is O(edges) instead of O(1). Far more complex
to implement and debug.
**Why rejected:** Unnecessary complexity for an AI training environment.

### Tile Map with Object Layer (like Tiled Editor)

**Advantages:** Industry standard, rich tooling, supports layers and metadata.
**Disadvantages:** External dependency, JSON/XML parsing, overkill for
our 9×16 grid.
**Why rejected:** We don't need an editor. The string representation is
sufficient and self-documenting.

## 9. Complexity Analysis

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| `world_to_grid()` | O(1) | Two integer divisions |
| `grid_to_world()` | O(1) | Two multiplications |
| `is_wall()` | O(1) | Bounds check + array lookup |
| `is_walkable()` | O(1) | 5 × `is_wall()` = 5 constant-time lookups |
| `reached_goal()` | O(1) | One distance calculation |
| `find_special_tiles()` | O(rows × cols) | Run once at initialization |
| `draw()` | O(rows × cols) | Run every frame |

The maze itself performs only constant-time spatial queries. Rendering
(`draw()` at O(rows × cols) every frame) remains the dominant maze-related
cost.

## 10. Interaction With Other Modules

```
Movement  ──reads──►  Maze.is_walkable()
Sensors   ──reads──►  Maze.is_wall()
Agent     ──reads──►  Maze.get_spawn()
Fitness   ──reads──►  Maze.reached_goal()
Renderer  ──calls──►  Maze.draw()
```

The maze is **read-only** during simulation. No module writes to it. This
makes it inherently thread-safe and stateless from the simulation's
perspective.

## 11. Future Improvements

- **Maze Loader** — Load layouts from `.txt` files for easy level swapping.
- **Procedural generation** — Recursive backtracking or Prim's algorithm.
- **Multiple goals** — Support several goal tiles for richer fitness signals.
- **Checkpoints** — Intermediate reward tiles for guiding evolution.
- **Dynamic obstacles** — Moving walls for advanced training scenarios.
