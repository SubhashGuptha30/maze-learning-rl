import random

import config
from neural_network.network import Network


class Genome:
    """A flat list of floats that represents a neural network's weights and biases.

    The genome is the bridge between evolution and the neural network.
    Evolution sees only numbers. It doesn't know about neurons or layers.
    The network sees only weights. It doesn't know about genomes or fitness.

    Genome → Network:  network.set_weights(genome.genes)
    Network → Genome:  genome.genes = network.get_weights()
    """

    def __init__(self, genes=None):
        if genes is not None:
            self.genes = list(genes)
        else:
            # Calculate total parameters: (inputs × hidden + hidden biases)
            #                           + (hidden × outputs + output biases)
            num_params = (
                (config.NETWORK_INPUTS * config.NETWORK_HIDDEN + config.NETWORK_HIDDEN)
                + (config.NETWORK_HIDDEN * config.NETWORK_OUTPUTS + config.NETWORK_OUTPUTS)
            )
            self.genes = [random.uniform(-1, 1) for _ in range(num_params)]

        self.fitness = 0.0

    def to_network(self):
        """Build a Network from this genome's genes."""
        net = Network(config.NETWORK_INPUTS, config.NETWORK_HIDDEN, config.NETWORK_OUTPUTS)
        net.set_weights(self.genes)
        return net

    def copy(self):
        """Return a deep copy of this genome."""
        clone = Genome(self.genes)
        clone.fitness = self.fitness
        return clone

    def __len__(self):
        return len(self.genes)
