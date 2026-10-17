# 07 — Neural Network

## 1. Purpose

The neural network is one possible implementation of the Brain interface.
It takes sensor readings as input and produces movement commands as output.
Unlike a rule-based brain that follows hand-coded logic, the neural network
learns its own strategy through evolution.

We build it from scratch — no TensorFlow, no PyTorch, no external ML
libraries. Just Python and math. This is deliberate: understanding every
neuron, every weight, every activation function is essential for debugging
evolution later.

## 2. Responsibilities

**Owns:**
- The forward pass (inputs → outputs).
- Network architecture (number of layers, neurons per layer).
- Activation functions.
- Weight and bias storage.

**Should Never Own:**
- Training (that's evolution's job — weights come from the genome).
- Sensor logic (it receives readings, it doesn't compute them).
- Movement physics (it outputs decisions, not displacements).
- Fitness evaluation.

## 3. Theory

### Why a Feedforward Network?

A feedforward network processes inputs in one direction: input → hidden →
output. There are no loops, no memory, no recurrence.

**Why not recurrent (RNN/LSTM)?** Recurrent networks have internal state
that persists between frames. This is powerful but dramatically increases
the genome size and makes evolution slower. For maze navigation, the
current sensor readings contain enough information to make a good decision.
The agent doesn't need to remember what it saw 10 frames ago.

**Why not convolutional (CNN)?** CNNs excel at spatial pattern recognition
in images. Our input is 5 floating-point numbers, not a 2D image. A CNN
would have nothing to convolve over.

### Why From Scratch?

Libraries like PyTorch optimize for backpropagation — computing gradients
and updating weights via gradient descent. We don't use gradient descent.
Our weights come from a genetic algorithm.

Building from scratch gives us:
1. **Full control** — We know exactly what every neuron does.
2. **Debugging transparency** — When an agent behaves oddly, we can inspect
   every weight, every activation, every intermediate value.
3. **Educational value** — Understanding neural networks at the neuron level
   is rare and valuable.
4. **No dependency** — The project runs with only `pygame` and Python's
   standard library.

### Why No Backpropagation?

Backpropagation requires:
1. A differentiable loss function.
2. Labeled training data (correct outputs for given inputs).
3. Gradient computation through the entire network.

We have none of these. There is no "correct" output for a given sensor
reading — the correct action depends on the maze, the goal, and the
agent's history. Fitness is evaluated over an entire lifetime, not per
decision.

Neuroevolution sidesteps this entirely: it treats the network as a black
box. If the agent with these weights survives longer and gets closer to the
goal, those weights are "good." No gradients needed.

### The Weight Space

A network with 6 inputs, 8 hidden neurons, and 4 outputs has:

```
Input → Hidden:   6 × 8 = 48 weights + 8 biases = 56
Hidden → Output:  8 × 4 = 32 weights + 4 biases = 36
Total: 92 parameters
```

(The 6th input is the direction to the goal; see 05_sensors.md.)

The genome is a flat list of 92 floating-point numbers. Evolution searches
this 92-dimensional space for the combination that produces the best
behavior.

Note: the Universal Approximation Theorem guarantees that a single hidden
layer can approximate any continuous function, given sufficient neurons.
This is why one hidden layer is a reasonable starting architecture.

## 4. Data Flow

```
Sensor Readings [0.0 – 1.0] (5 values)
        │
        ▼
Input Layer (5 neurons, no activation)
        │
        ▼
  weights × inputs + biases
        │
        ▼
Hidden Layer (N neurons, activation function)
        │
        ▼
  weights × hidden + biases
        │
        ▼
Output Layer (4 neurons, sigmoid)
        │
        ▼
Movement Commands [0.0 – 1.0] (4 values)
        │
        ▼
Threshold (> 0.5 = execute)
        │
        ├── outputs[0] → move forward
        ├── outputs[1] → move backward
        ├── outputs[2] → turn left
        └── outputs[3] → turn right
```

Note: opposing outputs (forward + backward, left + right) may both activate
simultaneously. Movement resolves this naturally — both commands are applied
independently, and opposing forces effectively cancel. Evolution will learn
to suppress conflicting outputs because they waste frames without progress.

## 5. Algorithm

### Single Neuron

```
FUNCTION neuron_output(inputs, weights, bias):
    sum ← 0
    FOR i IN range(len(inputs)):
        sum ← sum + inputs[i] × weights[i]
    sum ← sum + bias
    RETURN activation(sum)
```

### Layer Forward Pass

```
FUNCTION layer_forward(inputs, neurons):
    outputs ← []
    FOR EACH neuron IN neurons:
        value ← neuron_output(inputs, neuron.weights, neuron.bias)
        outputs.append(value)
    RETURN outputs
```

### Network Forward Pass

```
FUNCTION network_forward(inputs):
    current ← inputs
    FOR EACH layer IN layers:
        current ← layer_forward(current, layer)
    RETURN current
```

### Genome ↔ Network Conversion

```
FUNCTION unflatten(genome, architecture):
    pointer ← 0
    FOR EACH layer IN architecture:
        FOR EACH neuron IN layer:
            neuron.weights ← genome[pointer : pointer + input_count]
            pointer ← pointer + input_count
            neuron.bias ← genome[pointer]
            pointer ← pointer + 1

FUNCTION flatten(network):
    genome ← []
    FOR EACH layer IN network:
        FOR EACH neuron IN layer:
            genome.extend(neuron.weights)
            genome.append(neuron.bias)
    RETURN genome
```

## 6. Sequence of Operations

```
At Agent Creation
    │
    ├── Receive genome (flat float array) from evolution
    ├── Unflatten into Network (layers of neurons)
    └── Assign to agent's brain

Every Frame
    │
    ├── Read sensor values: [L, FL, F, FR, R]
    │
    ├── Forward pass through network
    │       ├── Input × weights + biases → hidden activations
    │       └── Hidden × weights + biases → output activations
    │
    ├── Interpret outputs: threshold at 0.5
    │       ├── output[0] > 0.5 → move_forward
    │       ├── output[1] > 0.5 → move_backward
    │       ├── output[2] > 0.5 → turn_left
    │       └── output[3] > 0.5 → turn_right
    │
    └── Issue commands to agent
```

## 7. Design Decisions

### Flat Genome Representation

All weights and biases are stored as a single flat list of floats.

**Why?** Crossover becomes trivially simple — pick a split point, take
the first half from parent A and the second half from parent B. Mutation
is just `genome[i] += random()`. The genome doesn't need to understand
network topology.

### Output Interpretation via Threshold

Each output is compared against 0.5. Above = execute the action.

**Why not argmax (pick the highest output)?** Argmax forces exactly one
action per frame. Threshold allows multiple simultaneous actions (e.g.,
move forward AND turn left = curved path). This gives the network richer
expressive power.

### Sigmoid on Output Layer

The output layer uses sigmoid activation, which squashes values to [0, 1].
This makes threshold comparison natural and prevents extreme output values.

**Why not tanh?** Tanh maps to [-1, 1]. We'd need to threshold at 0
instead of 0.5, and negative values have no intuitive meaning for our
binary actions.

## 8. Alternatives Considered

### Using PyTorch / TensorFlow

**Advantages:** Optimized matrix operations. GPU acceleration. Battle-tested.
**Disadvantages:** Massive dependency. Designed for backpropagation, not
neuroevolution. Opaque internals make debugging harder.
**Why rejected:** Educational value of from-scratch implementation. No
gradient computation needed. Keeps dependency list minimal.

### Recurrent Neural Network (RNN)

**Advantages:** Memory across frames. Can learn temporal patterns.
**Disadvantages:** Internal state increases genome size. Harder to evolve.
More complex forward pass. Risk of vanishing gradients (even in evolution,
sensitivity to initial state).
**Why deferred:** May explore later as a research-level improvement.

### Continuous Outputs (Steering + Throttle)

Instead of 4 binary actions, output 2 continuous values: steering angle
and speed.

**Advantages:** Smoother control. More natural movement.
**Disadvantages:** Requires redesigning the movement system to accept
continuous inputs. More complex output interpretation.
**Why deferred:** Binary actions match our current movement model. Can
revisit for advanced control.

## 9. Complexity Analysis

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| Single neuron | O(inputs) | Dot product + bias + activation |
| Single layer (N neurons, M inputs) | O(N × M) | N neurons, each O(M) |
| Full forward pass | O(Σ layers) | Sum of layer costs |
| 6→8→4 network | O(48 + 32) = O(80) | 80 weighted connections |
| 500 agents per frame | O(40,000) | 80 × 500 |

The neural network is extremely cheap. Even 500 forward passes per frame
add negligible computational cost compared to sensor raycasting.

## 10. Interaction With Other Modules

```
Genome (evolution)  ──creates──►  Network (unflatten)
                                    │
Sensors  ──provides readings──►  Network.forward()
                                    │
Network  ──outputs decisions──►  Agent (move/turn commands)
```

The network is a pure function: inputs in, outputs out. No side effects,
no state modification, no external queries.

## 11. Future Improvements

- **Multiple hidden layers** — Deeper networks for more complex behaviors.
- **Different activations per layer** — ReLU for hidden, sigmoid for output.
- **Weight initialization** — Xavier or He initialization for better
  starting points.
- **Network visualization** — Draw the network topology on screen, showing
  active neurons and weight magnitudes.
- **Recurrent connections** — Optional memory for temporal reasoning.
