import pygame

from agent.agent import Agent
from agent.input_controller import InputController
from agent.movement import Movement
from agent.sensors import SensorSystem
from environment.maze import Maze
from ui.debug_overlay import DebugOverlay
import config


def main():
    pygame.init()
    maze = Maze()
    agent = Agent(1, *maze.get_spawn(), movement=Movement(), sensors=SensorSystem())
    controller = InputController()
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
        agent.sensors.update(agent, maze)

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
