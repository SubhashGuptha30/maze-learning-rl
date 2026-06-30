# 08 — Evolution (Planned)

## Purpose

The evolution module implements a genetic algorithm that breeds populations
of neural networks. Instead of training with backpropagation, we evolve
weights through selection, crossover, and mutation — survival of the fittest.

## Planned Components

### Genome (`genome.py`)

A flat list of floats representing every weight and bias in a neural network.

```python
genome = [0.12, -0.45, 0.78, ...]  # all weights + biases flattened
```

The genome can be unflattened into a `Network` for evaluation, and a `Network`
can be flattened back into a genome for breeding.

### Mutation (`mutation.py`)

Small random perturbations to genome values:

```python
for i in range(len(genome)):
    if random() < mutation_rate:
        genome[i] += gauss(0, mutation_strength)
```

### Crossover (`crossover.py`)

Combines two parent genomes to produce offspring:

- **Single-point crossover**: Pick a random index, take genes from parent A
  before it and parent B after it.
- **Uniform crossover**: For each gene, randomly pick from parent A or B.

### Population (`population.py`)

Manages a generation of agents:

1. Evaluate fitness for all agents.
2. Select the best performers.
3. Breed offspring via crossover.
4. Apply mutation.
5. Replace the population.
6. Repeat.

## Planned Fitness Function

```
fitness = distance_toward_goal
        + checkpoint_bonus
        + time_alive_bonus
        - wall_collision_penalty
```

## Design Decisions (Planned)

- **Elitism** — The top N agents survive unchanged into the next generation.
  This ensures the best solution is never lost.
- **Tournament selection** — Pick K random agents, the fittest one becomes a
  parent. Simple, effective, and tunable.
- **Separation from the NN** — Evolution only sees flat float arrays. It
  doesn't know or care that they represent neural network weights.

## Future Improvements

- Speciation (NEAT-style) to protect innovation.
- Adaptive mutation rates.
- Hall of fame — store the best genome from each generation.
- Multi-objective fitness (Pareto-based selection).
