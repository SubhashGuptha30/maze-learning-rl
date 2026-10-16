from collections import deque

import config


def bfs_distance_map(maze):
    """Return a mapping of each reachable floor cell to its shortest path length from the goal in grid steps."""
    if maze.goal is None:
        return {}

    goal_row, goal_col = maze.world_to_grid(*maze.goal)
    distances = {(goal_row, goal_col): 0}
    queue = deque([(goal_row, goal_col)])

    while queue:
        row, col = queue.popleft()
        for delta_row, delta_col in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            next_row = row + delta_row
            next_col = col + delta_col
            if not (0 <= next_row < maze.rows and 0 <= next_col < maze.columns):
                continue
            if maze.is_wall(next_row, next_col):
                continue
            cell = (next_row, next_col)
            if cell in distances:
                continue
            distances[cell] = distances[(row, col)] + 1
            queue.append(cell)

    return distances


def path_distance(maze, distance_map, x, y):
    """Distance from a world point to the goal measured along corridors, in pixels."""
    if not distance_map:
        return float("inf")

    row, col = maze.world_to_grid(x, y)
    if (row, col) not in distance_map:
        # If the agent is in a wall or unreachable region, treat it as effectively far away.
        return float("inf")

    steps = distance_map[(row, col)]
    return steps * maze.cell_size


def evaluate_fitness(start_dist, final_dist, reached_goal, frames_used, max_frames):
    """Return a scalar fitness value where higher is better.

    progress     pixels of corridor distance closed toward the goal
    goal bonus   flat reward for reaching it, plus more the faster it got there
    Crashing and wandering are handled by the simulation: an agent that
    stops getting closer is stopped early and scored where it ended up.
    There is deliberately no per-crash penalty: it taught agents to stop in
    front of walls instead of turning, and they got stuck in the first corner.
    """
    fitness = max(0.0, start_dist - final_dist)

    if reached_goal:
        frames_left = max(0, max_frames - frames_used)
        fitness += config.GOAL_BONUS + config.SPEED_BONUS * frames_left / max(max_frames, 1)

    return fitness
