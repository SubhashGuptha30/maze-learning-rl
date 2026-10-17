# Feedforward Neural Networks

## What Is a Neural Network?

A neural network is a mathematical function that maps inputs to outputs
through layers of simple computations. Each layer transforms its input,
and the transformations are controlled by adjustable parameters called
**weights** and **biases**.

The learned behavior of a neural network is primarily encoded in its
weights. The architecture (how many layers, how many neurons) determines
the network's capacity — what it *could* learn. The weights define what
it *has* learned.

## The Neuron

The fundamental unit. A single neuron computes:

```
output = activation(w₁x₁ + w₂x₂ + ... + wₙxₙ + bias)
```

Where:
- `x₁...xₙ` are inputs (from the previous layer or from sensors).
- `w₁...wₙ` are weights (learned parameters).
- `bias` shifts the activation threshold.
- `activation` is a non-linear function (see Activation Functions).

Conceptually: a neuron computes a **weighted vote**. Each input contributes
its value multiplied by how important that input is (the weight). The bias
adjusts the baseline. The activation function decides whether the result
is "on" or "off."

## Layers

Neurons are organized into layers:

1. **Input layer** — Receives raw data (sensor readings). No computation.
   Each input neuron simply passes its value forward.
2. **Hidden layer(s)** — Transforms the input. This is where the network
   learns patterns. The number and size of hidden layers determines the
   network's capacity.
3. **Output layer** — Produces the final result (movement commands).

## The Forward Pass

Data flows in one direction: input → hidden → output. No loops, no
feedback. This is why it's called "feedforward."

```
Input:   [s₁, s₂, s₃, s₄, s₅]     ← 5 sensor readings

Hidden:  For each hidden neuron j:
           hⱼ = activation(Σᵢ wᵢⱼ × sᵢ + bⱼ)

Output:  For each output neuron k:
           oₖ = activation(Σⱼ wⱼₖ × hⱼ + bₖ)

Result:  [o₁, o₂, o₃, o₄]          ← 4 movement decisions
```

## The Weight Space

A network with 6 inputs, 8 hidden neurons, and 4 outputs has:

```
Input → Hidden:   6 × 8 weights + 8 biases = 56 parameters
Hidden → Output:  8 × 4 weights + 4 biases = 36 parameters
Total: 92 parameters
```

These 92 numbers define the network's entire behavior. Evolution searches
this 92-dimensional space for the combination that produces the best
maze-solving behavior.

## Why "Deep" Doesn't Always Mean "Better"

More layers = more parameters = larger genome = slower evolution. A single
hidden layer can approximate any continuous function (Universal
Approximation Theorem), given enough neurons. For maze navigation, one
hidden layer is sufficient.

## Feedforward vs. Recurrent

**Feedforward:** No memory. Each input is processed independently. The
network's output depends only on the current input.

**Recurrent:** Has internal state that persists between time steps. Can
remember previous inputs. More powerful but harder to train (especially
via evolution, where the genome must encode both weights and initial
state).

For our project, feedforward is sufficient. The current sensor readings
contain enough information to navigate. The agent doesn't need to remember
what it saw 10 frames ago.

## In Our Project

Our network takes 5 sensor readings, passes them through one hidden layer
of N neurons, and produces 4 output values (forward, backward, turn left,
turn right). Each output above 0.5 triggers the corresponding action.

The weights are not trained by backpropagation. They are set by the
genetic algorithm and evaluated by running the agent in the maze.
