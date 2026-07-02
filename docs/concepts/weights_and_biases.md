# Weights and Biases

## What Are Weights?

A weight is a number that controls how much influence one input has on a
neuron's output. Every connection between neurons has a weight.

```
input₁ ──[w₁]──┐
input₂ ──[w₂]──┤──► Σ ──► activation ──► output
input₃ ──[w₃]──┘
```

The neuron computes: `output = activation(w₁×x₁ + w₂×x₂ + w₃×x₃ + bias)`

A large positive weight means "this input strongly activates me."
A large negative weight means "this input strongly inhibits me."
A weight near zero means "I mostly ignore this input."

### Example: Maze Navigation

Imagine a neuron that decides whether to turn left. It receives 5 sensor
readings. If the right sensor detects a nearby wall, the agent should
turn left. So the weight connecting the right sensor to the "turn left"
neuron should be large and negative (closer wall = lower reading = turn
left).

The neural network doesn't know any of this in advance. Evolution
discovers these weight values through trial and error.

## What Are Biases?

A bias shifts the activation threshold of a neuron. It answers the
question: "How easily does this neuron fire?"

Without a bias, a neuron with zero inputs always outputs
`activation(0)`. The bias lets us shift this default:

```
output = activation(Σ(wᵢ × xᵢ) + bias)
                                   ↑
                            shifts the threshold
```

### Why Biases Are Necessary

Consider a simple case: we want a neuron that outputs 1 when the front
sensor is clear (reading > 0.7) and 0 otherwise.

Without bias, the neuron computes: `activation(w × sensor)`. For any
positive weight, this increases linearly with the sensor reading. We
can't create a threshold at 0.7 — we can only make the output
proportional to the input.

With bias: `activation(w × sensor + bias)`. By choosing `w = 10` and
`bias = -7`, we get `activation(10 × sensor - 7)`. When `sensor = 0.7`,
the argument is exactly 0, which is the midpoint of the sigmoid. Below
0.7, the output is near 0. Above 0.7, the output is near 1.

The bias creates the threshold.

### Intuitive Analogy

Think of a neuron as a switch with adjustable sensitivity:
- **Weights** control which inputs matter and how much.
- **Bias** controls how easy or hard it is to flip the switch.

A neuron with a large positive bias fires easily (even with weak inputs).
A neuron with a large negative bias is reluctant (requires strong inputs
to activate).

## Weights and Biases in Our Project

### Count

A 5→8→4 network has:
- 40 weights + 8 biases (input to hidden) = 48 parameters
- 32 weights + 4 biases (hidden to output) = 36 parameters
- Total: 84 parameters

### Storage

All 84 values are stored as a flat list of floats (the genome). Evolution
doesn't distinguish between weights and biases — they're all just numbers
to optimize.

### Initialization

In the first generation, all weights and biases are randomly initialized
(typically from a uniform or Gaussian distribution). This gives each agent
a unique but random brain. Most will be terrible. A few, by chance, will
be slightly less terrible. Evolution amplifies those.

## Common Misconceptions

**"Biases aren't important."** Without biases, the network can only learn
functions that pass through the origin. Adding biases lets the network
learn arbitrary offsets and thresholds.

**"More weights = smarter network."** More weights means a larger search
space for evolution. The GA must find the right value for every weight.
Doubling the weights roughly squares the search difficulty.

**"Weights are like importance rankings."** Not exactly. A weight's
meaning depends on the activation function, the bias, and the weights
in subsequent layers. Individual weights are not interpretable in
isolation.
