import random


def crossover(genes_a, genes_b):
    """Single-point crossover: child = a[:point] + b[point:].

    The point is in [1, len - 1] so the child always takes at least one
    gene from each parent. Both parents must be the same length.
    """
    if len(genes_a) != len(genes_b):
        raise ValueError("parents must have the same genome length")
    point = random.randint(1, len(genes_a) - 1)
    return genes_a[:point] + genes_b[point:]
