# Neuroevolution

## What Is Neuroevolution?

Neuroevolution is the combination of neural networks and evolutionary
algorithms. Instead of training a neural network with gradient descent
(backpropagation), we evolve its weights using a genetic algorithm.

The neural network provides the brain architecture. Evolution provides the
learning mechanism.

## Why Combine the Two?

### Neural networks need training

A randomly initialized neural network produces random outputs. To be
useful, its weights must be optimized. The standard approach is
backpropagation: compute the gradient of a loss function with respect to
each weight, and adjust weights in the direction that reduces loss.

But backpropagation requires:
1. A differentiable loss function.
2. Labeled training data (correct outputs for given inputs).
3. Per-step reward signals.

In many real-world scenarios — robotics, game playing, maze navigation —
these requirements aren't met. We don't know the "correct" action for a
given sensor reading. We only know whether the agent succeeded or failed
*overall*.

### Genetic algorithms need a representation

A genetic algorithm optimizes a vector of numbers. It doesn't care what
those numbers represent — they could be dimensions of a wing, parameters
of a chemical formula, or weights of a neural network.

Neural network weights are just numbers. A network with 84 parameters
becomes a point in 84-dimensional space. The GA searches this space for
the point that produces the best behavior.

## The Neuroevolution Loop

```
1. Create a population of random weight vectors (genomes)
2. For each genome:
     a. Build a neural network from the weights
     b. Run the agent in the simulation
     c. Evaluate fitness (distance to goal, survival time, etc.)
3. Select the fittest genomes
4. Produce offspring via crossover and mutation
5. Replace the population
6. Go to step 2
```

## Advantages Over Backpropagation

| Feature | Backpropagation | Neuroevolution |
|---------|----------------|----------------|
| Requires gradient | Yes | No |
| Requires labeled data | Yes | No |
| Per-step vs episodic | Per-step | Episodic |
| Handles non-differentiable objectives | No | Yes |
| Can optimize network topology | No (fixed) | Yes (NEAT) |
| Parallelization | Limited | Embarrassingly parallel |
| Sample efficiency | High | Low |

## Disadvantages

**Sample inefficiency:** Evolution requires many evaluations (generations
× population × frames) to converge. Backpropagation often converges with
far fewer samples.

**No per-step credit assignment:** If an agent makes 1000 decisions and
fails at step 999, evolution only sees "this genome scored poorly." It
can't tell which decision was wrong. Backpropagation assigns credit (or
blame) to each individual weight.

**Scalability limits:** Large networks have large genomes. The search
space grows exponentially with genome size. This is why neuroevolution
works best with small to medium networks.

## Famous Applications

- **NEAT (NeuroEvolution of Augmenting Topologies):** Evolves both weights
  and network topology. Used to play Mario, balance poles, and control
  robots.
- **OpenAI's Evolution Strategies:** Showed that evolution can compete with
  reinforcement learning on Atari games.
- **HyperNEAT:** Evolves a pattern-generating network that produces the
  actual network's weights. Enables very large networks.

## In Our Project

We use the simplest form of neuroevolution: fixed topology, evolving
weights only. Each genome is a flat list of 84 floats. The GA evaluates
fitness by running agents in the maze, then selects, crosses, and mutates
to produce the next generation.
