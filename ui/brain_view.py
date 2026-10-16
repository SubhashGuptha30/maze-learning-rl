import pygame

import config

INPUT_LABELS = ["L", "FL", "F", "FR", "R"]
OUTPUT_LABELS = ["FWD", "BACK", "LEFT", "RIGHT"]


class BrainView:
    """Draws a network as a node-link diagram: inputs -> hidden -> outputs.

    Lines are weights (green positive, red negative, brighter/thicker = larger).
    Nodes glow by activation (0..1). An output above 0.5 fires its action and
    gets a white ring.
    """

    WIDTH = 300

    def __init__(self):
        self.font = pygame.font.SysFont("Courier New", 13, bold=True)

    @staticmethod
    def _column(count, top, height):
        step = height / (count + 1)
        return [int(top + step * (i + 1)) for i in range(count)]

    @staticmethod
    def _weight_color(w):
        level = 70 + int(min(abs(w), 2.0) / 2.0 * 185)
        return (0, level, 0) if w > 0 else (level, 0, 0)

    def draw(self, screen, left, height, network, readings, title):
        pygame.draw.rect(screen, (20, 20, 30), (left, 0, self.WIDTH, height))
        screen.blit(self.font.render(title, True, config.WHITE), (left + 10, 8))

        top, body = 30, height - 30
        xs = (left + 55, left + 150, left + 235)
        layers_y = [
            self._column(network.num_inputs, top, body),
            self._column(network.num_hidden, top, body),
            self._column(network.num_outputs, top, body),
        ]

        # Re-run the forward pass layer by layer to get every activation
        inputs = list(readings) if readings else [0.0] * network.num_inputs
        hidden = network.hidden.forward(inputs)
        outputs = network.output.forward(hidden)
        activations = [inputs, hidden, outputs]

        for layer, (x0, x1) in zip((network.hidden, network.output), ((xs[0], xs[1]), (xs[1], xs[2]))):
            src_y = layers_y[0] if layer is network.hidden else layers_y[1]
            dst_y = layers_y[1] if layer is network.hidden else layers_y[2]
            for j, neuron in enumerate(layer.neurons):
                for i, w in enumerate(neuron.weights):
                    width = 1 + int(min(abs(w), 2.0))
                    pygame.draw.line(screen, self._weight_color(w), (x0, src_y[i]), (x1, dst_y[j]), width)

        for col, (x, ys, acts) in enumerate(zip(xs, layers_y, activations)):
            for k, (y, a) in enumerate(zip(ys, acts)):
                glow = int(255 * max(0.0, min(1.0, a)))
                pygame.draw.circle(screen, (glow, glow, 0), (x, y), 9)
                ring = config.WHITE if col == 2 and a > 0.5 else config.GRAY
                pygame.draw.circle(screen, ring, (x, y), 9, 2)
                if col == 0:
                    label = INPUT_LABELS[k] if k < len(INPUT_LABELS) else "GOAL"
                    screen.blit(self.font.render(label, True, config.WHITE), (x - 45, y - 7))
                elif col == 2:
                    screen.blit(self.font.render(OUTPUT_LABELS[k], True, config.WHITE), (x + 14, y - 7))
