import random

import config
from evolution.crossover import crossover
from evolution.genome import Genome
from evolution.mutation import mutate


class Population:
    """Holds the genomes of one generation and breeds the next one.

    The simulation writes genome.fitness; evolve() reads it.
    """

    def __init__(self, size=config.POPULATION_SIZE):
        self.genomes = [Genome() for _ in range(size)]
        self.generation = 1

    def tournament_select(self, k=config.TOURNAMENT_SIZE):
        """Pick k random genomes, return the fittest. Larger k = more selection pressure."""
        return max(random.sample(self.genomes, k), key=lambda g: g.fitness)

    def evolve(self):
        """Replace the population with the next generation."""
        ranked = sorted(self.genomes, key=lambda g: g.fitness, reverse=True)
        # Elitism: the best genomes survive unchanged, so the best score never drops.
        next_gen = [g.copy() for g in ranked[:config.ELITE_COUNT]]

        while len(next_gen) < len(self.genomes):
            child = crossover(self.tournament_select().genes, self.tournament_select().genes)
            next_gen.append(Genome(mutate(child, config.MUTATION_RATE, config.MUTATION_STRENGTH)))

        self.genomes = next_gen
        self.generation += 1
