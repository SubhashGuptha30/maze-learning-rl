# Genetic Algorithms

## What Is a Genetic Algorithm?

A genetic algorithm (GA) is an optimization technique inspired by natural
evolution. It maintains a population of candidate solutions, evaluates
their quality (fitness), and produces new solutions by combining and
mutating the best ones.

GAs don't know what they're optimizing. They don't compute gradients. They
don't understand the problem domain. They simply observe: "Solution A
scored 87. Solution B scored 43. Solution A is better. Make more solutions
like A." The population improves over generations through this selection
pressure.

## Core Concepts

### Population

A collection of candidate solutions. Each solution is called an
**individual** or **genome**. The population evolves as a whole — no single
individual "learns." Learning is an emergent property of the population.

### Fitness Function

A function that evaluates how good a solution is. The GA's only connection
to the problem domain. Everything else is domain-independent.

**Good fitness functions:**
- Reward progress (distance toward goal).
- Penalize waste (time, collisions).
- Are smooth (small improvements produce small fitness gains).

**Bad fitness functions:**
- Binary (reached goal = 1, didn't = 0). No gradient for evolution to
  follow.
- Noisy (same genome gets wildly different scores on different runs).

### Selection

Choosing which individuals become parents. Better individuals should be
more likely to reproduce, but not guaranteed — otherwise the population
loses diversity.

**Tournament selection:** Pick K random individuals, the fittest one wins.
Simple, effective, and selection pressure is controlled by K.

**Roulette wheel:** Probability proportional to fitness. Requires positive
fitness values. Sensitive to fitness scaling.

### Crossover

Combining two parent genomes to produce offspring. The idea: if parent A
is good at navigating corridors and parent B is good at turning corners,
their child might be good at both.

**Single-point:** Pick a random split. Child = parent_A[:split] +
parent_B[split:].

**Uniform:** For each gene, randomly pick from parent A or parent B.

### Mutation

Random perturbation of genes. Mutation introduces novelty that crossover
alone cannot produce. Without mutation, the population can only recombine
existing genetic material — it can never discover entirely new solutions.

**Gaussian mutation:** Add random noise from a normal distribution.
Most mutations are small; occasionally a large one occurs.

**Rate and strength:** Mutation rate controls how many genes change.
Mutation strength controls how much they change.

### Elitism

The top N individuals survive unchanged into the next generation. This
guarantees that the best solution found so far is never lost.

Without elitism, the best fitness can decrease between generations (a good
genome is destroyed by crossover/mutation). With elitism, best fitness is
monotonically non-decreasing.

## The Generational Loop

```
1. Initialize random population
2. Evaluate fitness for each individual
3. Select parents (tournament)
4. Create offspring (crossover)
5. Mutate offspring
6. Preserve elite individuals
7. Replace population
8. Go to step 2
```

## When to Use GAs

**Good fit:**
- The search space is large and complex.
- No gradient is available (non-differentiable objectives).
- The fitness function is expensive but evaluable.
- You need "good enough" solutions, not provably optimal ones.

**Bad fit:**
- The problem has a known analytical solution.
- Gradient information is readily available (use gradient descent).
- Real-time optimization is needed (GAs are slow per-iteration).

## In Our Project

Our GA optimizes neural network weights. Each genome is a flat list of
floats representing all weights and biases in a feedforward network.
Fitness is evaluated by running the agent in the maze and measuring how
close it gets to the goal.
