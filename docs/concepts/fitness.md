# Fitness Functions

## What Is Fitness?

Fitness is a single number that measures how well an individual (agent)
performed. It is the only signal the evolutionary algorithm receives.
Everything the GA knows about the quality of a solution comes from this
one number.

A well-designed fitness function is the most important part of a
neuroevolution system. A perfect neural network architecture with a bad
fitness function will learn the wrong thing. A simple architecture with
a good fitness function will learn the right thing.

## Properties of Good Fitness Functions

### Smooth (Gradient-Like)

A fitness function should reward partial progress, not just final success.

**Bad:** `fitness = 1 if reached_goal else 0`
In the first generations, no agent reaches the goal. Every agent gets
fitness 0. The GA has no signal to follow. It's searching blindly.

**Good:** `fitness = start_distance - current_distance`
Even in the first generation, agents that moved *toward* the goal score
higher than those that moved away. The GA has a gradient to follow.

### Decomposable

Complex behavior can be encouraged by combining multiple fitness
components:

```
fitness = distance_component
        + time_component
        + goal_bonus
        - collision_penalty
```

Each component provides a different signal. Together, they shape the
behavior the GA evolves.

### Stable

The same genome should produce roughly the same fitness across multiple
evaluations. High variance makes selection unreliable — a mediocre genome
might score high by luck and contaminate the gene pool.

If the environment has randomness (e.g., random spawn positions), evaluate
each genome multiple times and average.

## Common Fitness Components

### Distance to Goal

```
fitness += start_distance - final_distance
```

Rewards getting closer to the goal. The further the agent progresses, the
higher the fitness. This is the most important component — it gives the
GA a clear direction to optimize.

**Caution:** Euclidean distance alone can produce local optima in mazes
with walls. An agent may maximize fitness by pressing against the wall
closest to the goal rather than navigating around it. Checkpoints help
mitigate this (see below).

### Survival Time

```
fitness += frames_alive × survival_weight
```

Rewards staying alive longer. Useful early in evolution when agents
immediately crash into walls. Surviving longer means the agent has learned
basic obstacle avoidance.

**Danger:** If survival weight is too high, agents learn to stand still
(maximum survival time) instead of moving toward the goal.

### Goal Bonus

```
if reached_goal:
    fitness += GOAL_BONUS
```

A large one-time bonus for reaching the goal. This creates strong
selection pressure once some agents start reaching it.

### Blocked Movement Penalty

```
fitness -= rejected_moves × penalty_weight
```

Penalizes wall-hugging behavior. In our predictive collision system, no
actual collision occurs — movement is simply rejected. Counting rejected
moves measures how often the agent tried to enter a wall, which is a
proxy for poor steering.

### Efficiency

```
fitness += goal_bonus / time_taken
```

Rewards reaching the goal quickly. Without efficiency, agents might take
long, winding paths.

## Fitness Shaping

### The Problem of Deceptive Fitness

Sometimes the most direct path to the goal requires temporarily moving
*away* from it (e.g., going around a wall). A pure distance-based fitness
function punishes this detour, even though it's necessary.

### Checkpoints

Place intermediate reward points along the maze. Passing each checkpoint
adds to fitness. This guides evolution through the maze structure.

```
fitness += checkpoints_passed × checkpoint_bonus
```

### Novelty Search

Instead of rewarding fitness, reward *novelty* — how different an agent's
behavior is from all previous agents. This encourages exploration and can
overcome deceptive fitness landscapes.

## In Our Project

Our planned fitness function combines:
1. **Distance toward goal** — Primary signal.
2. **Survival time** — Rewards obstacle avoidance.
3. **Goal bonus** — Strong reward for completion.
4. (Future) **Checkpoint bonuses** — Guides through complex mazes.
5. (Future) **Collision penalties** — Discourages wall-hugging.
