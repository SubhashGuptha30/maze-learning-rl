import unittest

from environment.maze import Maze
from evolution.fitness import bfs_distance_map, evaluate_fitness, path_distance


class FitnessTests(unittest.TestCase):
    def test_bfs_distance_map_and_path_distance(self):
        maze = Maze()
        distances = bfs_distance_map(maze)

        goal_x, goal_y = maze.get_goal()
        self.assertIn((7, 14), distances)
        self.assertEqual(path_distance(maze, distances, goal_x, goal_y), 0)

    def test_evaluate_fitness_rewards_goal_and_progress(self):
        goal_score = evaluate_fitness(200, 0, True, 30, 200, 2)
        progress_score = evaluate_fitness(200, 80, False, 60, 200, 4)
        failure_score = evaluate_fitness(200, 200, False, 200, 200, 20)

        self.assertGreater(goal_score, progress_score)
        self.assertGreater(progress_score, failure_score)


if __name__ == "__main__":
    unittest.main()
