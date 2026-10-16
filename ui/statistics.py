import csv


class Statistics:
    """Per-generation numbers: best and average fitness, and how many agents reached the goal."""

    def __init__(self):
        self.history = []

    def record(self, generation, fitnesses, reached):
        row = {
            "generation": generation,
            "best": max(fitnesses),
            "average": sum(fitnesses) / len(fitnesses),
            "reached": reached,
        }
        self.history.append(row)
        return row

    def first_solved(self):
        """First generation in which at least one agent reached the goal, or None."""
        return next((r["generation"] for r in self.history if r["reached"]), None)

    def save_csv(self, path):
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["generation", "best", "average", "reached"])
            writer.writeheader()
            writer.writerows(self.history)

    @staticmethod
    def format(row, population_size):
        return (f"Gen {row['generation']:3d} | best {row['best']:8.1f} | "
                f"avg {row['average']:7.1f} | reached goal {row['reached']}/{population_size}")
