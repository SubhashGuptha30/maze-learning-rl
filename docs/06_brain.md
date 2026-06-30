# 06 — Brain (Controller Interface)

## Purpose

The "brain" is whatever decides how the agent moves each frame. Currently
this is the `InputController` (keyboard). Soon it will be a `NeuralNetwork`.

The key insight: **main.py should never know which brain is active.** Both
controllers expose the same interface:

```python
controller.update(agent, maze)
```

## Responsibilities

- **Owns**: Translating input (keyboard presses or neural network outputs)
  into agent commands (`move_forward`, `turn_left`, etc.).
- **Should never own**: Physics, sensors, rendering, or fitness evaluation.

## Current Implementation: InputController

```python
class InputController:
    def update(self, agent, maze):
        keys = pygame.key.get_pressed()
        if keys[K_w]:  agent.move_forward(maze)
        if keys[K_s]:  agent.move_backward(maze)
        if keys[K_a]:  agent.turn_left()
        if keys[K_d]:  agent.turn_right()
```

## Planned: Rule-Based Brain

Before the neural network, we'll implement a simple rule-based brain as a
**control experiment**:

```python
class RuleBasedBrain:
    def update(self, agent, maze):
        readings = agent.sensors.get_readings()
        front = readings[2]

        if front < 0.3:    # wall ahead
            agent.turn_right()
        else:
            agent.move_forward(maze)
```

This proves the controller interface works and gives us a baseline to compare
against the neural network.

## Planned: Neural Network Brain

```python
class NeuralNetworkBrain:
    def __init__(self, network):
        self.network = network

    def update(self, agent, maze):
        inputs = agent.sensors.get_readings()
        outputs = self.network.forward(inputs)
        # Interpret outputs as movement commands
```

## Design Decisions

- **Same interface for all brains** — `update(agent, maze)`. This means
  `main.py` never changes when we swap intelligence layers.
- **Brain doesn't own the agent** — It receives the agent as a parameter,
  issues commands, and returns. No persistent coupling.

## Future Improvements

- Hybrid controllers (keyboard override + neural network).
- Recording/playback controller for replays.
