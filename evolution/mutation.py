import random


def mutate(genes, rate, strength):
    """Return a copy of genes where each gene, with probability `rate`,
    gets Gaussian noise N(0, strength) added. Small tweaks are common,
    big jumps are rare."""
    return [g + random.gauss(0, strength) if random.random() < rate else g for g in genes]
