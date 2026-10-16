"""Run the GA over several seeds and report how many generations it takes to first reach the goal."""
import argparse
import statistics

from main import evolve
import config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=10)
    parser.add_argument("--max-generations", type=int, default=100)
    args = parser.parse_args()

    results = []
    for seed in range(args.seeds):
        stats = evolve(args.max_generations, config.POPULATION_SIZE, seed, stop_when_solved=True, verbose=False)
        solved = stats.first_solved()
        results.append(solved)
        print(f"seed {seed}: {'solved in generation ' + str(solved) if solved else 'not solved'}", flush=True)

    solved = [r for r in results if r is not None]
    print(f"\nSolved {len(solved)}/{args.seeds} seeds within {args.max_generations} generations "
          f"(population {config.POPULATION_SIZE}).")
    if solved:
        print(f"Generations to first solve: median {statistics.median(solved)}, "
              f"min {min(solved)}, max {max(solved)}")


if __name__ == "__main__":
    main()
