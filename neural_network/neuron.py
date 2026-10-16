import random

from neural_network.activation import sigmoid


class Neuron:
    """A single artificial neuron.

    Owns:
        - A list of weights (one per input).
        - A bias value.
        - An activation function.

    Computes:
        output = activation(Σ(weight_i × input_i) + bias)
    """

    def __init__(self, num_inputs, activation=sigmoid):
        # Random initial weights in [-1, 1]
        self.weights = [random.uniform(-1, 1) for _ in range(num_inputs)]
        self.bias = random.uniform(-1, 1)
        self.activation = activation

    def forward(self, inputs):
        """Compute the neuron's output for the given inputs."""
        if len(inputs) != len(self.weights):
            raise ValueError(
                f"Expected {len(self.weights)} inputs "
                f"but got {len(inputs)}"
            )

        weighted_sum = self.bias
        for weight, value in zip(self.weights, inputs):
            weighted_sum += weight * value

        return self.activation(weighted_sum)
