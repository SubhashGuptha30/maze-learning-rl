import json
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

    def save(self, path, generation=None):
        """Write the genes to a JSON file so a trained brain survives the program closing."""
        data = {
            "architecture": [config.NETWORK_INPUTS, config.NETWORK_HIDDEN, config.NETWORK_OUTPUTS],
            "generation": generation,
            "fitness": self.fitness,
            "genes": self.genes,
        }
        with open(path, "w") as f:
            json.dump(data, f)

    @classmethod
    def load(cls, path):
        """Read a genome saved by save(). Refuses a brain built for a different network shape."""
        with open(path) as f:
            data = json.load(f)
        expected = [config.NETWORK_INPUTS, config.NETWORK_HIDDEN, config.NETWORK_OUTPUTS]
        if data.get("architecture") != expected or len(data.get("genes", [])) != len(cls()):
            raise ValueError(f"{path} was saved for network {data.get('architecture')}, "
                             f"but config.py now builds {expected}")
        genome = cls(data["genes"])
        genome.fitness = data.get("fitness", 0.0)
        return genome

