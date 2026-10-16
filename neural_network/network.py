from neural_network.layer import Layer


class Network:
    """A feedforward neural network: input → hidden → output.

    Owns:
        - A hidden Layer.
        - An output Layer.

    Computes:
        outputs = output_layer.forward(hidden_layer.forward(inputs))

    The input layer is implicit — the raw inputs are passed directly
    to the hidden layer without transformation.
    """

    def __init__(self, num_inputs, num_hidden, num_outputs):
        self.num_inputs = num_inputs
        self.num_hidden = num_hidden
        self.num_outputs = num_outputs
        self.hidden = Layer(num_hidden, num_inputs)
        self.output = Layer(num_outputs, num_hidden)

    def forward(self, inputs):
        """Run a complete forward pass: inputs → hidden → outputs."""
        hidden_out = self.hidden.forward(inputs)
        return self.output.forward(hidden_out)

    def get_weights(self):
        """Flatten all weights and biases into a single list.

        Order: hidden layer (neuron by neuron: weights then bias),
               then output layer (same order).

        This is the genome representation for evolution.
        """
        flat = []
        for layer in [self.hidden, self.output]:
            for neuron in layer.neurons:
                flat.extend(neuron.weights)
                flat.append(neuron.bias)
        return flat

    def set_weights(self, flat):
        """Load weights and biases from a flat list (genome).

        Inverse of get_weights(). Same ordering.
        """
        idx = 0
        for layer in [self.hidden, self.output]:
            for neuron in layer.neurons:
                num_w = len(neuron.weights)
                neuron.weights = flat[idx:idx + num_w]
                idx += num_w
                neuron.bias = flat[idx]
                idx += 1
