from neural_network.neuron import Neuron


class Layer:
    """A collection of neurons that all receive the same inputs.

    Owns:
        - A list of Neuron objects.

    Computes:
        outputs = [neuron.forward(inputs) for each neuron]
    """

    def __init__(self, num_neurons, num_inputs_per_neuron, activation=None):
        if activation is not None:
            self.neurons = [Neuron(num_inputs_per_neuron, activation) for _ in range(num_neurons)]
        else:
            self.neurons = [Neuron(num_inputs_per_neuron) for _ in range(num_neurons)]

    def forward(self, inputs):
        """Pass inputs through every neuron and return their outputs."""
        return [neuron.forward(inputs) for neuron in self.neurons]
