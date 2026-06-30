# 07 — Neural Network (Planned)

## Purpose

A from-scratch feedforward neural network that maps sensor readings to
movement commands. No external ML libraries — built entirely with Python
and `math`.

## Planned Architecture

```
Input Layer (5 neurons)     ← sensor readings [0.0 – 1.0]
       │
Hidden Layer (N neurons)    ← ReLU or tanh activation
       │
Output Layer (4 neurons)    ← forward, backward, turn_left, turn_right
```

## Planned Components

### Neuron (`neuron.py`)

A single neuron:
```
output = activation( Σ(weight_i × input_i) + bias )
```

### Layer (`layer.py`)

A collection of neurons. Handles the forward pass for one layer.

### Network (`network.py`)

Chains layers together. Exposes `forward(inputs) → outputs`.

## Key Design Decisions (Planned)

- **No backpropagation** — Weights will be set by the genetic algorithm, not
  gradient descent. This is neuroevolution, not supervised learning.
- **Flat weight vector** — The genome will store all weights as a flat list.
  The network will unflatten them into layers. This makes crossover and
  mutation trivially simple.
- **Deterministic** — Given the same weights and inputs, the output is always
  the same. No dropout, no stochastic elements during evaluation.

## Future Improvements

- Multiple hidden layers.
- Different activation functions per layer.
- Weight initialization strategies (Xavier, He).
