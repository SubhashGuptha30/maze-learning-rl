import pygame


class InputController:
    """Translates keyboard input into agent commands.

    This decouples the input source from the agent. Later, when a neural
    network replaces the keyboard, main.py won't need to change — we'll
    simply swap the controller.
    """

    def update(self, agent, maze):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            agent.move_forward(maze)
        if keys[pygame.K_s]:
            agent.move_backward(maze)
        if keys[pygame.K_a]:
            agent.turn_left()
        if keys[pygame.K_d]:
            agent.turn_right()
