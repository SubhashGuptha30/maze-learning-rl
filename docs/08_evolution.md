# 08 — Evolution

## 1. Purpose

Evolution is the training algorithm. It replaces backpropagation. Instead of
computing gradients and adjusting weights mathematically, it breeds
populations of neural networks, keeps the ones that perform best, and
discards the rest.

This is neuroevolution: the combination of neural networks and evolutionary
algorithms. The neural network provides the brain architecture; evolution
provides the learning mechanism.

Without evolution, we'd have randomly initialized neural networks that
never improve. Evolution is what makes them learn.

## 2. Responsibilities

**Owns:**
- Managing a population of genomes.
- Evaluating fitness.
- Selecting parents.
- Producing offspring via crossover and mutation.
- Generational lifecycle (create → evaluate → select → breed → repeat).

**Should Never Own:**
- Neural network forward pass (that's the network's job).
- Agent physics or sensors (those belong to the simulation).
- Rendering or visualization.
- Maze structure.

## 3. Theory

### Why Neuroevolution Instead of Q-Learning or Backpropagation?

**Q-Learning** requires defining a discrete state space (every possible
configuration the agent can be in) and a reward signal for every action.
In a continuous 2D world with floating-point positions, the state space
is infinite. Discretizing it loses precision.

**Backpropagation** requires labeled data: "given these sensor readings,
the correct action is X." We don't have correct actions — we only have
outcomes (did the agent reach the goal?). The correct action at any given
moment depends on the agent's entire future trajectory, which we can't
compute in advance.

**Neuroevolution** only requires a fitness function: "how well did this
agent do overall?" It doesn't need per-step labels. It doesn't need a
discrete state space. It treats the neural network as a black box and
optimizes its weights through selection pressure.

### The Genotype-Phenotype Mapping

In biology:
- **Genotype** = DNA (the code).
- **Phenotype** = The organism (the expression of the code).

In our system:
- **Genotype** = A flat list of floats (the genome).
- **Phenotype** = A neural network with those weights (the brain).

Evolution operates on genotypes. Fitness is evaluated on phenotypes.
This separation is crucial: evolution doesn't know what a neural network
is. It only knows that some float arrays produce fitter agents than others.

### Selection Pressure

The fundamental insight of evolution: if better individuals are more likely
to reproduce, the population improves over time.

**Too much pressure** (only the #1 agent reproduces) → loss of diversity →
premature convergence → stuck in local optima.

**Too little pressure** (everyone reproduces equally) → no selection →
random drift → no improvement.

The balance is achieved through tournament selection and elitism.

### Elitism

The top N agents survive unchanged into the next generation.

**Why?** Without elitism, the best solution discovered so far can be
destroyed by crossover or mutation. Elitism guarantees that the best
genome found so far is always preserved in the population.

## 4. Data Flow

```
Generation N
    │
    ├── Create agents from genomes
    ├── Simulate (each agent runs in the maze)
    ├── Evaluate fitness for each agent
    │
    ▼
Selection
    │
    ├── Rank by fitness
    ├── Elite agents survive unchanged
    ├── Tournament selection for parents
    │
    ▼
Breeding
    │
    ├── Crossover: combine two parent genomes
    ├── Mutation: perturb offspring genes
    │
    ▼
Generation N+1 (repeat)
```

### Generation Lifetime

Each generation runs until one of two conditions is met:

1. **Frame limit** — A maximum number of frames (e.g., 1000) have elapsed.
   This ensures evaluation terminates even if agents are stuck.
2. **All agents terminated** — Every agent has been marked inactive (e.g.,
   timeout or inactivity). The specific termination conditions are a
   design decision documented in [02_agent.md](02_agent.md) § Future
   Improvements.

Whichever comes first ends the generation. All surviving agents are
evaluated at that point. The frame limit is a tuning parameter: too short
and agents can't reach the goal; too long and evolution wastes time on
hopeless agents.

## 5. Algorithm

### Fitness Evaluation

```
FUNCTION evaluate_fitness(agent, maze):
    fitness ← 0

    — Distance toward goal (closer = higher fitness)
    start_distance ← distance(spawn, goal)
    current_distance ← distance(agent.position, goal)
    fitness ← fitness + (start_distance - current_distance)

    — Bonus for reaching the goal
    IF maze.reached_goal(agent):
        fitness ← fitness + GOAL_BONUS

    — Bonus for survival time
    fitness ← fitness + frames_alive × SURVIVAL_WEIGHT

    RETURN fitness
```

### Tournament Selection

```
FUNCTION tournament_select(population, k):
    candidates ← random_sample(population, k)
    RETURN candidate with highest fitness
```

### Single-Point Crossover

```
FUNCTION crossover(parent_a, parent_b):
    point ← random_integer(1, genome_length - 1)
    child ← parent_a[0:point] + parent_b[point:]
    RETURN child
```

### Mutation

```
FUNCTION mutate(genome, rate, strength):
    FOR i IN range(len(genome)):
        IF random() < rate:
            genome[i] ← genome[i] + gaussian(0, strength)
    RETURN genome
```

### Generational Loop

```
FUNCTION evolve(population):
    — Evaluate
    FOR EACH agent IN population:
        agent.fitness ← evaluate_fitness(agent, maze)

    — Sort by fitness (descending)
    sort(population, by=fitness, descending=True)

    — Elitism: keep top N unchanged
    next_generation ← population[0:elite_count]

    — Breed the rest
    WHILE len(next_generation) < population_size:
        parent_a ← tournament_select(population, k)
        parent_b ← tournament_select(population, k)
        child ← crossover(parent_a.genome, parent_b.genome)
        child ← mutate(child, mutation_rate, mutation_strength)
        next_generation.append(child)

    RETURN next_generation
```

## 6. Sequence of Operations

```
Program Start
    │
    ▼
Initialize random population of N genomes
    │
    ▼
┌─► Create agents from genomes (unflatten → networks → brains)
│       │
│       ▼
│   Simulate for T frames
│       │
│       ├── Each frame: brain.update() → movement → sensors
│       └── Track: distance to goal, time alive, collisions
│       │
│       ▼
│   Evaluate fitness for all agents
│       │
│       ▼
│   Select parents (tournament)
│       │
│       ▼
│   Breed offspring (crossover + mutation)
│       │
│       ▼
│   Elitism: preserve top performers
│       │
│       ▼
│   Replace population
│       │
└───────┘ (repeat for G generations)
```

## 7. Design Decisions

### Tournament Selection Over Roulette Wheel

**Tournament:** Pick K random agents, the fittest wins.
**Roulette:** Probability of selection proportional to fitness.

**Why tournament?**
1. Doesn't require fitness to be positive (roulette does).
2. Selection pressure is controlled by K (tournament size), not fitness
   scale.
3. Simpler to implement. No normalization needed.

### Flat Genome, Not Structured

The genome is a flat list of floats, not a tree or graph.

**Why?** Crossover on flat arrays is trivial. Pick a split point, take
halves from each parent. On structured representations, crossover risks
producing invalid offspring (e.g., mismatched layer sizes).

**Trade-off:** Flat genomes can't evolve network topology (number of
layers, neurons). This limits our search to weight optimization within a
fixed architecture. NEAT-style topology evolution would require structured
genomes.

### Gaussian Mutation

Mutations add Gaussian noise: `gene += gaussian(0, strength)`.

**Why Gaussian?** Most mutations are small (near the mean). Occasionally,
a large mutation occurs (in the tails). This mirrors biological mutation:
small changes are common, radical changes are rare but possible.

**Why not uniform?** Uniform noise gives every magnitude equal probability.
This makes small refinements as likely as large disruptions, which slows
convergence.

### Separation of Genome and Network

The genome (flat floats) and the network (neurons, layers) are separate
representations of the same information.

**Why?** Evolution operates on genomes. Simulation operates on networks.
They need different interfaces. Keeping them separate means evolving the
genome never requires importing neural network code, and running the
network never requires importing evolution code.

## 8. Alternatives Considered

### Reinforcement Learning (Q-Learning, Policy Gradient)

**Advantages:** Mathematically grounded. Per-step reward signals. Well-
studied convergence guarantees.
**Disadvantages:** Requires discrete state space (Q-learning) or
differentiable policy (policy gradient). Both assume structure we don't
have.
**Why rejected:** Our environment is continuous, our reward is episodic
(end-of-life fitness), and our network is a black box. Neuroevolution
fits these constraints naturally.

### NEAT (NeuroEvolution of Augmenting Topologies)

**Advantages:** Evolves both weights AND topology. Protects innovation
through speciation. State-of-the-art in neuroevolution.
**Disadvantages:** Significantly more complex. Requires historical
markings, speciation, and compatibility distance calculations.
**Why deferred:** Start simple with fixed topology. If results plateau,
NEAT is a natural next step.

### Coevolution

**Advantages:** Agents compete against each other, creating an arms race.
**Disadvantages:** Requires multi-agent interaction. Fitness becomes
relative, not absolute. Much harder to debug.
**Why deferred:** Single-agent maze solving is hard enough. Coevolution
is a research-level extension.

## 9. Complexity Analysis

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| Fitness evaluation | O(T × N) | T frames × N agents |
| Sorting by fitness | O(N log N) | Standard sort |
| Tournament selection | O(K) | K = tournament size |
| Crossover | O(genome_length) | One array splice |
| Mutation | O(genome_length) | One pass through genome |
| Full generation | O(T × N + N log N + N × G) | T dominates |

With N=500 agents, T=1000 frames, genome=84 floats:
- Simulation: 500,000 frames of physics + sensing
- Sorting: negligible
- Breeding: 500 × 84 ≈ 42,000 operations

The simulation is the bottleneck, not evolution.

## 10. Interaction With Other Modules

```
Evolution  ──creates──►  Genomes (flat float arrays)
              │
              ▼
           Unflatten  ──creates──►  Networks
              │
              ▼
           Networks   ──assigned to──►  Agents (as brains)
              │
              ▼
           Simulation ──produces──►  Fitness scores
              │
              ▼
           Evolution  ──reads──►  Fitness ──►  Selection + Breeding
```

Evolution sits above the simulation. It creates the conditions, lets them
play out, observes the results, and iterates.

## 11. Future Improvements

- **Speciation** — NEAT-style. Protect innovation by grouping similar
  genomes and allowing them to compete within groups.
- **Adaptive mutation** — Reduce mutation strength as fitness plateaus,
  then increase if stuck.
- **Hall of fame** — Store the best genome from each generation. Enables
  replays and regression testing.
- **Multi-objective fitness** — Pareto-based selection optimizing distance,
  speed, and efficiency simultaneously.
- **Island model** — Multiple sub-populations evolving independently, with
  occasional migration. Prevents premature convergence.
