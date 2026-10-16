# 09 — Fitness Evaluation

## 1. Purpose

The Fitness Evaluator measures how well an agent performed during its
lifetime. It produces a single scalar value — the fitness score — that
the evolutionary algorithm uses to rank agents and select parents.

Fitness is the *only* signal evolution receives. Everything the genetic
algorithm knows about the quality of a neural network comes from this
one number. A well-designed fitness function is more important than a
well-designed network architecture.

## 2. Responsibilities

**Owns:**
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

Implemented in `evolution/fitness.py`:

```
fitness = (start_path_dist - final_path_dist)
        + (GOAL_BONUS + SPEED_BONUS × frames_left / MAX_FRAMES)   if goal reached
```

Distances are BFS path distances on the grid (computed once from the goal),
not Euclidean, so walls don't make an agent look closer than it is.
There is no blocked-movement penalty. An earlier version charged 0.5 per
move rejected by a wall; it taught agents to stop in front of walls rather
than turn, and 6 of 10 seeds got stuck in the first corner. Removing it
(together with a goal-direction input) fixed that — see the README results.
Survival time is deliberately not rewarded: wandering agents are stopped
after `STUCK_FRAMES` without getting closer and scored where they stopped.
Efficiency is the speed bonus; checkpoints are unnecessary because BFS
distance already gives a gradient through every corridor.
