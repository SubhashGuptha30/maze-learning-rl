# 09 — Fitness Evaluation (Planned)

## 1. Purpose

The Fitness Evaluator measures how well an agent performed during its
lifetime. It produces a single scalar value — the fitness score — that
the evolutionary algorithm uses to rank agents and select parents.

Fitness is the *only* signal evolution receives. Everything the genetic
algorithm knows about the quality of a neural network comes from this
one number. A well-designed fitness function is more important than a
well-designed network architecture.

## 2. Responsibilities

**Will Own:**
- Computing a fitness score from agent lifetime data (distance traveled,
  time survived, goal reached, blocked movements).
- Combining multiple fitness components with configurable weights.
- Providing the interface between simulation and evolution.

**Should Never Own:**
- Agent movement or physics.
- Neural network weights or forward pass.
- Selection or breeding (that's evolution's job).

## 3. Planned Fitness Components

| Component | Signal | Purpose |
|-----------|--------|---------|
| Distance toward goal | `start_dist - final_dist` | Primary gradient for evolution |
| Survival time | `frames_alive × weight` | Rewards obstacle avoidance |
| Goal bonus | `+GOAL_BONUS if reached` | Strong reward for completion |
| Blocked movement penalty | `-rejected_moves × weight` | Discourages wall-hugging |
| Efficiency | `bonus / time_taken` | Rewards fast solutions |
| Checkpoints | `+bonus per checkpoint` | Guides through complex mazes |

## 4. Design Considerations

See [concepts/fitness.md](concepts/fitness.md) for detailed discussion of:
- Smooth vs. binary fitness functions.
- Deceptive fitness and local optima.
- Euclidean distance limitations in mazes with walls.
- Novelty search as an alternative.

## Status

This module does not yet exist in code. It will be implemented as part of
the evolution system. The fitness evaluation algorithm is documented in
[08_evolution.md](08_evolution.md) § Algorithm § Fitness Evaluation.
