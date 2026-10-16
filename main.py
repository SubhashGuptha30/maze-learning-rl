import pygame

from agent.agent import Agent
from agent.neural_network_brain import NeuralNetworkBrain
from agent.movement import Movement
from agent.sensors import SensorSystem
from environment.maze import Maze
from neural_network.network import Network
from ui.debug_overlay import DebugOverlay
import config


def main():
    pygame.init()
    maze = Maze()
    agent = Agent(1, *maze.get_spawn(), movement=Movement(), sensors=SensorSystem())
    network = Network(config.NETWORK_INPUTS, config.NETWORK_HIDDEN, config.NETWORK_OUTPUTS)
    controller = NeuralNetworkBrain(network)
    screen = pygame.display.set_mode((maze.width, maze.height))
    pygame.display.set_caption(config.WINDOW_TITLE)

    clock = pygame.time.Clock()
    overlay = DebugOverlay()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update
        controller.update(agent, maze)
        agent.update(maze)

        # Draw
        screen.fill(config.BLACK)
        maze.draw(screen)
        agent.sensors.draw(screen, agent)
        agent.draw(screen)
        overlay.draw(screen, agent, clock)

        pygame.display.flip()
        clock.tick(config.FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
