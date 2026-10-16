import argparse
import os
import random

from agent.agent import Agent
from agent.neural_network_brain import NeuralNetworkBrain
from environment.maze import Maze
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


def evolve(generations, population_size, seed, renderer=None, stop_when_solved=False, verbose=True,
           save_path=None, seed_genome=None):
    """Run the genetic algorithm. Returns the Statistics history.

    If save_path is given, the best genome so far is written there after every
    generation, so closing the window never loses the trained brain.
    """
    random.seed(seed)
    maze = Maze()
    distance_map = bfs_distance_map(maze)
    population = Population(population_size, seed_genome)
    best_ever = None
    stats = Statistics()

    for _ in range(generations):
        last = stats.history[-1] if stats.history else None
        hud = f"Gen {population.generation}"
        if last:
            hud += f" | best {last['best']:.0f} avg {last['average']:.0f}"

        reached = run_generation(population.genomes, maze, distance_map, renderer, hud)
        if reached is None:
            break

        row = stats.record(population.generation, [g.fitness for g in population.genomes], reached)
        best = max(population.genomes, key=lambda g: g.fitness)
        if save_path and (best_ever is None or best.fitness > best_ever.fitness):
            best_ever = best.copy()
            best_ever.save(save_path, population.generation)
        if verbose:
            print(Statistics.format(row, population_size))
        if stop_when_solved and reached:
            break
        population.evolve()

    return stats


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
    args = parser.parse_args()

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
        renderer = Renderer(Maze())

    stats = evolve(args.generations, args.population, args.seed, renderer,
                   save_path=args.brain, seed_genome=seed_genome)

    if renderer is not None:
        renderer.close()
    if args.csv:
        stats.save_csv(args.csv)
    print(f"First generation to reach the goal: {stats.first_solved()}")
    print(f"Best brain saved to {args.brain}")


if __name__ == "__main__":
    main()
