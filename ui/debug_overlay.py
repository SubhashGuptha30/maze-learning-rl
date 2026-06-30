import math
import pygame
import config


class DebugOverlay:
    def __init__(self):
        self.font = pygame.font.SysFont("Courier New", 14)
        self.text_color = config.WHITE
        self.bg_color = (0, 0, 0, 150) # Semi-transparent black

    def draw(self, screen, agent, clock, generation="-", fitness="-"):
        info_lines = [
            f"FPS: {int(clock.get_fps())}",
            f"Generation: {generation}",
            f"Fitness: {fitness}",
            "",
            f"Agent ID: {agent.id}",
            f"Alive: {agent.alive}",
            f"Position: ({agent.x:.1f}, {agent.y:.1f})",
            f"Angle: {math.degrees(agent.angle):.1f}°",
            f"Speed: {agent.speed}",
            "",
            "Sensors:",
        ]

        # Add sensor readings nicely
        sensor_names = ["Left", "Front Left", "Front", "Front Right", "Right"]
        for name, reading in zip(sensor_names, agent.sensors.get_readings()):
            info_lines.append(f"  {name:<12} {reading:.2f}")

        # Render background surface
        line_height = self.font.get_linesize()
        padding = 10
        width = 250
        height = len(info_lines) * line_height + 2 * padding
        
        overlay_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay_surf.fill(self.bg_color)

        for i, line in enumerate(info_lines):
            text_surf = self.font.render(line, True, self.text_color)
            overlay_surf.blit(text_surf, (padding, padding + i * line_height))

        screen.blit(overlay_surf, (10, 10))
