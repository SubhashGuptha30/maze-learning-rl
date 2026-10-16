import pygame

import config
from ui.debug_overlay import DebugOverlay


class Renderer:
    """Draws the maze, every active agent and a HUD strip below the maze.

    The leader (closest to the goal) is drawn in yellow with its sensors.
    Press D to toggle the debug overlay for the leader.
    """

    HUD_HEIGHT = 28

    def __init__(self, maze):
        pygame.init()
        self.screen = pygame.display.set_mode((maze.width, maze.height + self.HUD_HEIGHT))
        pygame.display.set_caption(config.WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Courier New", 16, bold=True)
        self.overlay = DebugOverlay()
        self.show_debug = False

    def handle_events(self):
        """Return False when the window is closed."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_d:
                self.show_debug = not self.show_debug
        return True

    def draw(self, maze, agents, leader, hud_text, generation="-"):
        self.screen.fill(config.BLACK)
        maze.draw(self.screen)
        for agent in agents:
            agent.color = config.YELLOW if agent is leader else config.RED
            agent.draw(self.screen)
        leader.sensors.draw(self.screen, leader)

        text = self.font.render(hud_text, True, config.WHITE)
        self.screen.blit(text, (8, maze.height + 5))
        if self.show_debug:
            self.overlay.draw(self.screen, leader, self.clock, generation)

        pygame.display.flip()
        self.clock.tick(config.FPS)

    def save_screenshot(self, path):
        pygame.image.save(self.screen, path)

    def close(self):
        pygame.quit()
