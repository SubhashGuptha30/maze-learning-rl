# Design Decisions

This document records the major design decisions in the project, their
rationale, the alternatives considered, and the trade-offs accepted.

---

## Decision #1 — NeuroEvolution Instead of Q-Learning

**Context:** We need an algorithm to train agents to navigate a maze.

**Decision:** Use neuroevolution (genetic algorithm + neural network).

**Alternatives considered:**
- **Q-Learning:** Requires a discrete state space. Our world is continuous
  (floating-point positions, angles). Discretizing it loses precision and
  creates an exponentially large state table.
- **Deep Q-Network (DQN):** Uses a neural network to approximate Q-values,
  avoiding the state table. However, DQN still requires per-step reward
  signals, a replay buffer, and a target network. More infrastructure than
  neuroevolution for a comparable result in our domain.
- **Policy Gradient / Deep RL:** Requires a differentiable loss function
  and per-step reward signals. Our reward is episodic (did the agent
  reach the goal?), not per-action.
- **Backpropagation on the neural network:** Requires labeled training
  data (correct output for each input). We don't know the correct action
  for a given sensor reading — it depends on the entire future trajectory.

**Why neuroevolution?** It only needs a fitness function. It treats the
network as a black box. It works naturally with continuous state spaces,
episodic rewards, and non-differentiable objectives.

---

## Decision #2 — Five Sensors

**Context:** How many sensor rays should the agent have?

**Decision:** Five sensors at -90°, -45°, 0°, +45°, +90°.

**Alternatives considered:**
- **Three sensors** (left, front, right): Lacks diagonal awareness. Agent
  can't distinguish "wall ahead-left" from "wall directly left."
- **Eight or more sensors:** More inputs → more weights → larger genome →
  slower evolution. Diminishing returns on spatial awareness.
- **Full 360° sweep:** Maximum awareness but massive input vector. The
  neural network would need far more weights to process it.

**Why five?** Sweet spot between spatial awareness and input dimensionality.
The agent has peripheral, diagonal, and forward coverage. The resulting
network has a small, fast-to-evolve genome. A sixth input, the direction
to the goal, was added later; see 05_sensors.md.

---

## Decision #3 — Normalized Sensor Values [0, 1]

**Context:** What format should sensor readings be in?

**Decision:** Normalize all readings to [0.0, 1.0].

**Alternatives considered:**
- **Raw pixel distances [0, 200]:** Different scale from other potential
  inputs. Network weights for sensors would need to be 200× smaller than
  weights for other inputs. Uneven learning landscape.
- **Boolean (wall/no wall):** Loses distance information. The agent can't
  distinguish "wall is 10 pixels away" from "wall is 100 pixels away."

**Why normalized?** All inputs are on the same scale. The genome search
space is uniform. The network treats all sensors equally. Standard practice
in machine learning.

---

## Decision #4 — No Backpropagation

**Context:** How should neural network weights be updated?

**Decision:** Weights are set by the genetic algorithm, not by gradient
descent.

**Rationale:** Backpropagation requires:
1. A differentiable loss function (we have a non-differentiable fitness).
2. Labeled data (we have no "correct" outputs).
3. Gradient computation (unnecessary overhead for our approach).

Neuroevolution doesn't need any of these. It evaluates the entire agent
lifetime and assigns a scalar fitness. No per-step gradients, no loss
functions, no training/test splits.

---

## Decision #5 — Flat Genome Representation

**Context:** How should neural network weights be stored for evolution?

**Decision:** As a single flat list of floating-point numbers.

**Alternatives considered:**
- **Structured genome** (preserving layer boundaries): More complex
  crossover. Must ensure layer sizes match between parents.
- **Tree-based genome** (like genetic programming): Allows topology
  evolution but requires specialized crossover and mutation operators.

**Why flat?** Crossover is trivially simple: pick a split point, take
halves from each parent. Mutation is one loop: `gene += gaussian()`.
Evolution doesn't need to understand neural network structure.

**Trade-off:** Can't evolve network topology (number of layers/neurons).
Only weights change. Acceptable for a fixed architecture; revisit with
NEAT if results plateau.

---

## Decision #6 — Modular Controller Interface

**Context:** How should the agent receive movement commands?

**Decision:** All brains implement `update(agent, maze)`. The simulation
doesn't know which brain is active.

**Alternatives considered:**
- **Agent subclasses** (KeyboardAgent, AIAgent): Can't swap brains at
  runtime. Population management requires multiple class types.
- **Event-based control:** Brain publishes events, agent subscribes.
  Powerful but requires event bus infrastructure. Overkill.

**Why a uniform interface?** Strategy pattern. Swap one line in main.py
to change the entire intelligence layer. The game loop, maze, sensors,
and movement code never change.

---

## Decision #7 — Step-Based Ray Casting

**Context:** How should sensor rays detect walls?

**Decision:** Advance each ray pixel-by-pixel and check `is_wall()` at
each step.

**Alternatives considered:**
- **DDA (Digital Differential Analyzer):** Jumps directly to cell
  boundaries. O(cells_crossed) instead of O(pixels). Faster for long
  ranges.
- **Analytical ray-segment intersection:** Compute exact intersection
  with wall edges. Most accurate but requires geometric computation for
  every nearby wall segment.

**Why step-based?** Simplest to implement, debug, and understand. At
max_range=200 with step=1, we do at most 200 checks per ray — all O(1)
grid lookups. The total cost (5 × 200 = 1000 lookups per agent) is
negligible.

**When to revisit:** If we scale to 1000+ agents or increase max_range
significantly, DDA becomes worthwhile.

---

## Decision #8 — Predictive Collision (Reject, Not Correct)

**Context:** What happens when an agent tries to move into a wall?

**Decision:** Check the destination before moving. If invalid, the agent
stays put. No wall sliding, no push-back.

**Alternatives considered:**
- **Corrective collision:** Move first, detect overlap, push agent back.
  Requires penetration depth, contact normals, and cascading resolution.
- **Wall sliding:** Project rejected velocity onto the wall tangent.
  Smoother for human play but teaches AI to lean on walls.

**Why predictive rejection?** Clean signal for the neural network. "This
direction is blocked" = movement was rejected. No ambiguity. No hidden
physics the network must learn. Deterministic and simple.

---

## Decision #9 — Delegation Over Inheritance

**Context:** How should the agent be structured?

**Decision:** The agent holds state and delegates behavior to Movement,
SensorSystem, and Brain components.

**Alternatives considered:**
- **God object:** Agent does everything. Simple initially, unmaintainable
  at scale.
- **Pure ECS (Entity-Component-System):** Maximum flexibility but requires
  a component registry, system scheduler, and message passing. Overkill.

**Why delegation?** 80% of ECS benefit with 20% of the complexity. We can
swap Movement implementations, change sensor configurations, and replace
brains — all without modifying the Agent class.

---

## Decision #10 — Grid-Based World

**Context:** How should the maze be represented?

**Decision:** A 2D string grid where each character is a tile type.

**Alternatives considered:**
- **Continuous 2D space with polygons:** More realistic but requires
  computational geometry. Collision becomes O(edges) instead of O(1).
- **Tile map editor format (Tiled/JSON):** Industry standard but requires
  external tools and parsing. Overkill for our 9×16 grid.

**Why string grid?** O(1) spatial lookups. Self-documenting (you can see
the maze in the source code). No external dependencies. Perfect for an AI
training environment where speed matters more than visual fidelity.
