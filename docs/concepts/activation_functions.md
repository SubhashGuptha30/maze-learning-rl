# Activation Functions

## Why Activation Functions?

Without activation functions, a neural network is just a series of linear
transformations: `output = W₂ × (W₁ × input + b₁) + b₂`. This collapses
to a single linear function: `output = W × input + b`. No matter how many
layers you add, the network can only learn linear relationships.

Activation functions introduce **non-linearity**. This allows the network
to learn curves, thresholds, and complex decision boundaries that a linear
function cannot represent.

## Common Activation Functions

### Sigmoid

```
σ(x) = 1 / (1 + e^(-x))
```

**Output range:** (0, 1)
**Shape:** S-curve. Smoothly transitions from 0 to 1.
**Derivative:** σ(x) × (1 - σ(x)). Maximum at x=0, vanishes at extremes.

**Pros:**
- Output is bounded [0, 1]. Natural for probability-like outputs.
- Smooth and differentiable everywhere.

**Cons:**
- Vanishing gradient at extreme values (saturates). Neurons can "die" and
  stop learning.
- Output is always positive (not centered at zero).

**Use in our project:** Output layer. Each output represents "should this
action happen?" The [0, 1] range maps naturally to a threshold at 0.5.

### Tanh (Hyperbolic Tangent)

```
tanh(x) = (e^x - e^(-x)) / (e^x + e^(-x))
```

**Output range:** (-1, 1)
**Shape:** S-curve centered at zero.
**Derivative:** 1 - tanh²(x). Same vanishing problem as sigmoid at
extremes, but gradient is stronger near zero.

**Pros:**
- Zero-centered output. Better for hidden layers because the mean
  activation is near zero, which helps the next layer.
- Stronger gradients than sigmoid near x=0.

**Cons:**
- Still saturates at extreme values.
- Slightly more expensive to compute than ReLU.

**Use in our project:** Good candidate for hidden layers.

### ReLU (Rectified Linear Unit)

```
ReLU(x) = max(0, x)
```

**Output range:** [0, ∞)
**Shape:** Zero for negative inputs, linear for positive inputs.
**Derivative:** 0 for x < 0, 1 for x > 0.

**Pros:**
- Extremely fast to compute (one comparison).
- No vanishing gradient for positive values.
- Promotes sparsity (many neurons output zero). This advantage is
  primarily important in gradient-based learning; in neuroevolution,
  where we don't compute gradients, it matters less.

**Cons:**
- "Dying ReLU" problem: if a neuron's input is always negative, it
  permanently outputs zero and never recovers.
- Unbounded output can cause numerical instability.

**Use in our project:** Good candidate for hidden layers if we want speed.

## Which One Should We Use?

For neuroevolution (no backpropagation), the vanishing gradient problem
is irrelevant — we don't compute gradients. The choice comes down to:

1. **Output layer → Sigmoid.** We need outputs in [0, 1] for threshold
   comparison. Sigmoid is the natural choice.

2. **Hidden layer → Tanh or ReLU.** Both work. Tanh gives bounded,
   zero-centered outputs. ReLU is faster and promotes sparsity.

For our initial implementation, **tanh for hidden layers and sigmoid for
output** is a sensible default. Evolution will find weights that work with
whatever activation we choose.

## The Key Insight

The activation function determines the **shape of the decision boundary**
the network can learn. Linear activation = flat boundary. Sigmoid/tanh =
curved boundary. The more expressive the activation, the more complex the
behaviors the network can represent — but also the harder the genome search
becomes.

For maze navigation, simple curves are sufficient. We don't need the
expressive power of a deep network with exotic activations. One hidden
layer with tanh is enough.
