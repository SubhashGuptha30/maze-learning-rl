import random

from environment.maze import Maze
from environment.maze_generator import generate_layout
from evolution.crossover import crossover
from evolution.fitness import bfs_distance_map, evaluate_fitness, path_distance
from evolution.genome import Genome
from evolution.mutation import mutate
from evolution.population import Population

# Fixed copy of the original maze, so tests don't change when you edit environment/maze.py
ORIGINAL_LAYOUT = [
    "################",
    "#S.............#",
    "#.#####.######.#",
    "#..............#",
    "#.#######.####.#",
    "#..............#",
    "#.#######.####.#",
    "#.............G#",
    "################",
]


def test_crossover_keeps_genome_length_and_mixes_parents():
    random.seed(1)
    a, b = [0.0] * 84, [1.0] * 84
    for _ in range(100):
        child = crossover(a, b)
        assert len(child) == 84
        # single point: a prefix of a-genes then a suffix of b-genes, at least one of each
        assert child[0] == 0.0 and child[-1] == 1.0
        assert child == sorted(child)


def test_mutation_changes_genes_at_expected_rate():
    random.seed(2)
    genes = [0.0] * 20000
    mutated = mutate(genes, rate=0.1, strength=0.5)
    changed = sum(g != 0.0 for g in mutated) / len(genes)
    assert 0.09 < changed < 0.11
    assert genes == [0.0] * 20000  # original is not modified


def test_mutation_rate_zero_changes_nothing():
    genes = [0.3] * 100
    assert mutate(genes, rate=0.0, strength=1.0) == genes


def test_elitism_keeps_best_genome():
    random.seed(3)
    population = Population(size=20)
    for i, genome in enumerate(population.genomes):
        genome.fitness = float(i)
    best = list(population.genomes[-1].genes)

    population.evolve()

    assert len(population.genomes) == 20
    assert population.genomes[0].genes == best
    assert population.generation == 2


def test_fitness_is_higher_closer_to_goal():
    maze = Maze(ORIGINAL_LAYOUT)
    distances = bfs_distance_map(maze)
    start = path_distance(maze, distances, *maze.get_spawn())
    near = path_distance(maze, distances, *maze.grid_to_world(7, 12))  # two cells from G
    far = path_distance(maze, distances, *maze.grid_to_world(1, 2))    # next to spawn

    assert near < far < start
    assert evaluate_fitness(start, near, False, 500, 1000) > evaluate_fitness(start, far, False, 500, 1000)


def test_bfs_uses_corridor_distance_not_straight_line():
    maze = Maze(ORIGINAL_LAYOUT)
    distances = bfs_distance_map(maze)
    # (1, 14) is 6 rows straight above G (7, 14) along the right-hand corridor
    assert distances[(1, 14)] == 6
    assert distances[(1, 1)] == 19  # spawn: Manhattan path around the walls
    assert (0, 0) not in distances  # walls are never reachable


def test_genome_round_trips_through_network():
    genome = Genome()
    assert genome.to_network().get_weights() == genome.genes


def test_genome_save_and_load_round_trip(tmp_path):
    genome = Genome()
    genome.fitness = 123.0
    path = tmp_path / "brain.json"
    genome.save(path, generation=7)

    loaded = Genome.load(path)
    assert loaded.genes == genome.genes
    assert loaded.fitness == 123.0


def test_population_seeded_from_saved_brain_keeps_it_first():
    random.seed(4)
    brain = Genome()
    population = Population(size=10, seed_genome=brain)
    assert population.genomes[0].genes == brain.genes
    assert len(population.genomes) == 10
    assert any(g.genes != brain.genes for g in population.genomes[1:])


def test_generated_maze_is_perfect_and_solvable():
    for name in ("a", "b", "c"):
        layout = generate_layout(rng=random.Random(name))
        maze = Maze(layout)
        distances = bfs_distance_map(maze)
        floor_cells = sum(row.count(".") + row.count("S") + row.count("G") for row in layout)
        assert len(distances) == floor_cells           # every open cell connects to the goal
        assert maze.world_to_grid(*maze.get_spawn()) in distances
        # perfect maze = a tree: number of open-cell adjacencies is cells - 1 (no loops)
        edges = sum(1 for (r, c) in distances for (dr, dc) in ((1, 0), (0, 1)) if (r + dr, c + dc) in distances)
        assert edges == floor_cells - 1


def test_generated_maze_is_reproducible_from_name():
    assert generate_layout(rng=random.Random("x")) == generate_layout(rng=random.Random("x"))
    assert generate_layout(rng=random.Random("x")) != generate_layout(rng=random.Random("y"))
