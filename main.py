import pygame

from agent.agent import Agent
from agent.movement import Movement
from agent.sensors import SensorSystem
from environment.maze import BLACK, Maze


def main():
    pygame.init()
    maze = Maze()
    agent = Agent(1, *maze.get_spawn(), movement=Movement(), sensors=SensorSystem())
    screen = pygame.display.set_mode((maze.width, maze.height))
    pygame.display.set_caption("Reinforcement Learning Maze")

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            agent.move_forward(maze)
        if keys[pygame.K_s]:
            agent.move_backward(maze)
        if keys[pygame.K_a]:
            agent.turn_left()
        if keys[pygame.K_d]:
            agent.turn_right()

        agent.sensors.update(agent, maze)

        screen.fill(BLACK)
        maze.draw(screen)
        agent.sensors.draw(screen, agent)
        agent.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
