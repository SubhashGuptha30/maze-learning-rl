# Architecture Overview

## Project Structure

```
RL/
├── config.py                 # Global configuration constants
├── main.py                   # Entry point and game loop
│
├── agent/
│   ├── agent.py              # Agent entity (state + delegation)
│   ├── movement.py           # Physics: turning and translation
│   ├── sensors.py            # Raycasting sensor system
│   └── input_controller.py   # Keyboard → agent command translator
│
├── environment/
│   ├── maze.py               # Grid-based maze world
│   ├── tile.py               # Tile type constants
│   └── collision.py          # (Reserved) Advanced collision logic
│
├── neural_network/           # (Planned) From-scratch feedforward NN
│   ├── neuron.py
│   ├── layer.py
│   └── network.py
│
├── evolution/                # (Planned) Neuroevolution / genetic algorithm
│   ├── genome.py
│   ├── mutation.py
│   ├── crossover.py
│   └── population.py
│
├── ui/
│   └── debug_overlay.py      # Real-time telemetry HUD
│
└── docs/                     # This documentation folder
```

## Data Flow

```
InputController / NeuralNetwork
        │
        ▼
      Agent  ──►  Movement  ──►  Maze.is_walkable()
        │
        ▼
   SensorSystem  ──►  Maze.is_wall()
        │
        ▼
   Normalized Readings [0.0 – 1.0]
        │
        ▼
   (Future) Neural Network Input
```

## Design Principles

1. **Single Responsibility** — Each class owns exactly one concern.
2. **Swappable Controllers** — `InputController` and a future `NeuralNetworkBrain`
   share the same interface (`update(agent, maze)`), so `main.py` never changes.
3. **Centralized Configuration** — All magic numbers live in `config.py`.
4. **Separation of Intelligence from Physics** — The agent doesn't know how it
   decides to move; it only knows that something tells it to.

## Planned Architecture (Post-AI)

```
Simulation
├── World
│   ├── Maze
│   └── Agents[]
├── Population
│   ├── Genomes[]
│   └── FitnessEvaluator
├── Evolution
│   ├── Mutation
│   └── Crossover
├── Statistics
└── Renderer
```
