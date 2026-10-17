import argparse
import os
import random

from agent.agent import Agent
from agent.neural_network_brain import NeuralNetworkBrain
from environment.maze import Maze
from environment.maze_generator import generate_layout, generate_track
from evolution.fitness import bfs_distance_map, evaluate_fitness, path_distance
from evolution.genome import Genome
from evolution.population import Population
from ui.statistics import Statistics
import config


def run_generation(genomes, maze, distance_map, renderer=None, hud_prefix=""):
    """Simulate one agent per genome, then write each genome's fitness.

    An agent stops when it reaches the goal, when it hasn't got closer to the
    goal for STUCK_FRAMES frames, or at MAX_FRAMES. Returns how many agents
    reached the goal, or None if the window was closed.
    """
    spawn = maze.get_spawn()
    start_dist = path_distance(maze, distance_map, *spawn)
    n = len(genomes)
    agents = [Agent(i, *spawn) for i in range(n)]
    brains = [NeuralNetworkBrain(g.to_network()) for g in genomes]
    best_dist = [start_dist] * n
    frames_since_progress = [0] * n
    frames_used = [0] * n
    reached = [False] * n

    for frame in range(1, config.MAX_FRAMES + 1):
        active = [i for i in range(n) if agents[i].alive]
        if not active:
            break

        for i in active:
            agent = agents[i]
            brains[i].update(agent, maze)
            agent.update(maze)
            frames_used[i] = frame

            dist = path_distance(maze, distance_map, agent.x, agent.y)
            if dist < best_dist[i]:
                best_dist[i] = dist
                frames_since_progress[i] = 0
            else:
                frames_since_progress[i] += 1

            if maze.reached_goal(agent):
                reached[i] = True
                agent.alive = False
            elif frames_since_progress[i] >= config.STUCK_FRAMES:
                agent.alive = False

        if renderer is not None:
            if not renderer.handle_events():
                return None
            leader = min(active, key=lambda i: best_dist[i])
            hud = f"{hud_prefix} | alive {len(active)} | reached {sum(reached)}"
            renderer.draw(maze, agents, agents[leader], brains[leader].network, hud)

    for i, genome in enumerate(genomes):
        final_dist = path_distance(maze, distance_map, agents[i].x, agents[i].y)
        genome.fitness = evaluate_fitness(start_dist, final_dist, reached[i],
                                          frames_used[i], config.MAX_FRAMES)
    return sum(reached)


VALIDATION_SIZE = 10  # fixed layouts that pick which brain to save in multi-layout training


def random_maze(name, kind="track"):
    """A generated track or maze; the same name always gives the same layout."""
    generate = generate_track if kind == "track" else generate_layout
    return Maze(generate(rng=random.Random(name)))


def run_on_mazes(genomes, mazes, renderer=None, hud_prefix=""):
    """Score every genome on each maze and set its fitness to the average.

    Returns the total number of goal reaches over all mazes, or None if the
    window was closed.
    """
    totals = [0.0] * len(genomes)
    reached = 0
    for k, maze in enumerate(mazes):
        hud = hud_prefix if len(mazes) == 1 else f"{hud_prefix} | maze {k + 1}/{len(mazes)}"
        result = run_generation(genomes, maze, bfs_distance_map(maze), renderer, hud)
        if result is None:
            return None
        reached += result
        for i, genome in enumerate(genomes):
            totals[i] += genome.fitness
    for i, genome in enumerate(genomes):
        genome.fitness = totals[i] / len(mazes)
    return reached


def evolve(generations, population_size, seed, renderer=None, stop_when_solved=False, verbose=True,
           save_path=None, seed_genome=None, train_mazes=0, kind="track"):
    """Run the genetic algorithm. Returns the Statistics history.

    train_mazes=0 trains on the fixed maze in environment/maze.py. train_mazes=K
    scores every agent on K new random layouts (`kind`: "track" or "maze") each
    generation, so memorising one layout stops paying off and only general
    driving skill survives.

    If save_path is given, the best genome of every generation is written there,
    so closing the window never loses the trained brain. With random layouts
    that score is noisy, so instead the generation's best drives a fixed
    validation set and is saved only when it beats the best validation score.
    """
    random.seed(seed)
    fixed_maze = [Maze()] if not train_mazes else None
    population = Population(population_size, seed_genome)
    stats = Statistics()
    runs_per_generation = population_size * max(train_mazes, 1)
    validation = [random_maze(f"val-{i}", kind) for i in range(VALIDATION_SIZE)] if train_mazes else None
    best_validation = -1

    for _ in range(generations):
        last = stats.history[-1] if stats.history else None
        hud = f"Gen {population.generation}"
        if last:
            hud += f" | best {last['best']:.0f} avg {last['average']:.0f}"

        mazes = fixed_maze or [random_maze(f"train-{seed}-{population.generation}-{k}", kind)
                               for k in range(train_mazes)]
        reached = run_on_mazes(population.genomes, mazes, renderer, hud)
        if reached is None:
            break

        row = stats.record(population.generation, [g.fitness for g in population.genomes], reached)
        best = max(population.genomes, key=lambda g: g.fitness)
        line = Statistics.format(row, runs_per_generation)
        if validation:
            # Evaluate a copy: running it overwrites fitness, which evolve() still needs
            solved = sum(run_generation([best.copy()], m, bfs_distance_map(m)) for m in validation)
            line += f" | validation {solved}/{len(validation)}"
            if solved > best_validation:
                best_validation = solved
                if save_path:
                    best.save(save_path, population.generation)
        elif save_path:
            # Elitism keeps this generation's best, so on a fixed maze this never gets worse
            best.save(save_path, population.generation)
        if verbose:
            print(line)
        if stop_when_solved and reached:
            break
        population.evolve()

    return stats


def test_brain(genome, count, renderer=None, kind="track"):
    """Run one brain, without evolving it, on `count` random layouts it was never
    trained on. Returns how many it solved."""
    solved = 0
    for i in range(count):
        maze = random_maze(f"test-{i}", kind)
        reached = run_generation([genome], maze, bfs_distance_map(maze), renderer, f"Test maze {i + 1}/{count}")
        if reached is None:
            break
        solved += reached
    return solved


def main():
    parser = argparse.ArgumentParser(description="Evolve neural-network agents to solve a maze.")
    parser.add_argument("--headless", action="store_true", help="no window, runs as fast as possible")
    parser.add_argument("--generations", type=int, default=config.GENERATIONS)
    parser.add_argument("--population", type=int, default=config.POPULATION_SIZE)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--csv", help="save per-generation statistics to this CSV file")
    parser.add_argument("--brain", default="best_brain.json",
                        help="saved brain: continued from if it exists, then updated (default: %(default)s)")
    parser.add_argument("--fresh", action="store_true",
                        help="ignore the saved brain and start from random ones (overwrites it)")
    parser.add_argument("--train-mazes", type=int, default=0, metavar="K",
                        help="train on K new random layouts per generation instead of the fixed maze")
    parser.add_argument("--kind", choices=["track", "maze"], default="track",
                        help="random layouts for --train-mazes/--test: race tracks or dead-end mazes")
    parser.add_argument("--test", type=int, metavar="N",
                        help="don't evolve: run the saved brain on N unseen random mazes and report")
    args = parser.parse_args()

    if args.test:
        if not os.path.exists(args.brain):
            parser.error(f"--test needs a trained brain, but {args.brain} doesn't exist")
        renderer = None
        if not args.headless:
            from ui.renderer import Renderer
            renderer = Renderer(random_maze("test-0", args.kind))
        solved = test_brain(Genome.load(args.brain), args.test, renderer, args.kind)
        if renderer is not None:
            renderer.close()
        print(f"Solved {solved}/{args.test} unseen {args.kind}s")
        return

    seed_genome = None
    if not args.fresh and os.path.exists(args.brain):
        try:
            seed_genome = Genome.load(args.brain)
        except ValueError as e:
            parser.error(f"{e}. Run with --fresh to start over.")
        print(f"Continuing from saved brain {args.brain} (use --fresh to start from scratch)")
    else:
        print("Starting from random brains")

    renderer = None
    if not args.headless:
        from ui.renderer import Renderer
        renderer = Renderer(random_maze("size", args.kind) if args.train_mazes else Maze())

    stats = evolve(args.generations, args.population, args.seed, renderer,
                   save_path=args.brain, seed_genome=seed_genome, train_mazes=args.train_mazes, kind=args.kind)

    if renderer is not None:
        renderer.close()
    if args.csv:
        stats.save_csv(args.csv)
    print(f"First generation to reach the goal: {stats.first_solved()}")
    print(f"Best brain saved to {args.brain}")


if __name__ == "__main__":
    main()
