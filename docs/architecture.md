# Architecture

## High-Level Overview

This project is an AI simulation engine. Agents navigate a maze, sense
their environment through raycasting, and are controlled by swappable
brains (keyboard, rules, or neural networks). Neural network weights are
optimized via a genetic algorithm — no backpropagation, no gradient descent.

```
┌──────────────────────────────────────────┐
│              Simulation Loop             │
│                                          │
│  ┌──────────┐    ┌───────┐    ┌──────┐  │
│  │  Brain    │───►│ Agent │───►│ Maze │  │
│  │(Controller)│   │       │◄───│      │  │
│  └──────────┘    └───┬───┘    └──────┘  │
│                      │                   │
│               ┌──────┴──────┐            │
│               │  Sensors    │            │
│               └─────────────┘            │
│                                          │
└──────────────────────────────────────────┘
         ▲                    │
         │   Fitness Scores   │
         │                    ▼
┌──────────────────────────────────────────┐
│              Evolution                   │
│                                          │
│  Selection → Crossover → Mutation        │
│                                          │
│  Genome (flat floats) ↔ Network (layers) │
└──────────────────────────────────────────┘
```

## Runtime Flow

```
Program Start
    │
    ▼
pygame.init()
    │
    ▼
Create Maze (parse layout, find spawn + goal)
    │
    ▼
Create Agent(s) at spawn position
    │
    ▼
Create Controller (keyboard / rule-based / neural)
    │
    ▼
┌──► Game Loop ──────────────────────────────┐
│       │                                     │
│       ├── Process pygame events (quit)      │
│       ├── controller.update(agent, maze)    │
│       ├── agent.update(maze)                │
│       │       └── sensors.update()          │
│       ├── Draw: maze → sensors → agent → overlay │
│       ├── pygame.display.flip()             │
│       └── clock.tick(FPS)                   │
│                                             │
└─────────────────────────────────────────────┘
    │
    ▼
pygame.quit()
```

## Frame Update Flow (Single Frame)

```
┌─────────────────────────────────────────────────────┐
│                    ONE FRAME                         │
│                                                      │
│  1. Events     pygame.event.get() → check QUIT      │
│                                                      │
│  2. Input      controller.update(agent, maze)        │
│                  └─► turn / move commands             │
│                                                      │
│  3. Physics    Movement checks maze.is_walkable()    │
│                  └─► accept or reject position        │
│                                                      │
│  4. Sensing    agent.update(maze)                    │
│                  └─► sensors cast 5 rays              │
│                  └─► normalize distances              │
│                                                      │
│  5. Render     screen.fill() → maze → sensors →      │
│                agent → overlay → flip                 │
│                                                      │
│  6. Timing     clock.tick(FPS)                       │
│                                                      │
└─────────────────────────────────────────────────────┘
```

## Training Flow (Planned)

```
Initialize population of N random genomes
    │
    ▼
┌──► FOR EACH generation ──────────────────────────┐
│       │                                           │
│       ├── Create N agents from genomes            │
│       │     └── unflatten genome → network        │
│       │                                           │
│       ├── Simulate T frames                       │
│       │     └── brain.update → move → sense       │
│       │     └── track distance, time, blocked moves  │
│       │                                           │
│       ├── Evaluate fitness                        │
│       │     └── distance + survival + goal bonus  │
│       │                                           │
│       ├── Selection                               │
│       │     └── tournament select parents         │
│       │                                           │
│       ├── Breeding                                │
│       │     └── crossover + mutation → children   │
│       │                                           │
│       ├── Elitism                                 │
│       │     └── preserve top K genomes unchanged  │
│       │                                           │
│       └── Replace population                      │
│                                                   │
└───────────────────────────────────────────────────┘
```

## Data Flow

```
Maze Layout (strings)
      │
      ▼
Spatial Queries (is_wall, is_walkable, reached_goal)
      │
      ├───────────────────────────┐
      ▼                           ▼
  Movement                    Sensors
  (collision check)           (raycasting)
      │                           │
      ▼                           ▼
  Agent State                 Readings [0-1]
  (x, y, angle)                   │
                                  ▼
                              Brain (NN)
                                  │
                                  ▼
                           Movement Commands
                                  │
                                  ▼
                           Agent State Update
                                  │
                                  ▼
                           Fitness Evaluation
                                  │
                                  ▼
                              Evolution
                                  │
                                  ▼
                           Next Generation
```

## Folder Structure

```
RL/
├── config.py                 Global constants (one source of truth)
├── main.py                   Entry point: generation loop, CLI flags
├── benchmark.py              Runs the GA over many seeds
│
├── agent/
│   ├── agent.py              Entity: state + delegation
│   ├── movement.py           Physics: turning + translation
│   ├── sensors.py            Perception: raycasting + normalization
│   ├── input_controller.py   Brain: keyboard → commands
│   ├── rule_based_brain.py   Brain: hand-written rules
│   └── neural_network_brain.py Brain: network outputs → commands
│
├── environment/
│   ├── maze.py               World: grid + spatial queries + collision
│   ├── tile.py               Constants: wall, floor, spawn, goal
│   └── maze_generator.py     Random perfect mazes and closed-loop race tracks
│
├── neural_network/           From-scratch feedforward NN
│   ├── activation.py         Sigmoid
│   ├── neuron.py             Single neuron: weights + bias + activation
│   ├── layer.py              Collection of neurons
│   └── network.py            Chains layers: forward pass
│
├── evolution/                Genetic algorithm
│   ├── fitness.py            BFS path distance + fitness score
│   ├── genome.py             Flat float array ↔ network conversion
│   ├── mutation.py           Gaussian perturbation of genes
│   ├── crossover.py          Combining parent genomes
│   └── population.py         Generational lifecycle
│
├── ui/
│   ├── debug_overlay.py      Real-time telemetry HUD (press D)
│   ├── renderer.py           Draws population + generation HUD
│   ├── brain_view.py         Live network diagram of the leader's brain
│   └── statistics.py         Best/avg/reached per generation, CSV export
│
├── tests/                    pytest: GA operators and fitness
│
└── docs/                     Documentation (you are here)
    ├── architecture.md       This file
    ├── design_decisions.md   Why the project looks the way it does
    ├── 01_environment.md     Through 09_fitness.md
    └── concepts/             Concept explanations (not code docs)
        ├── activation_functions.md
        ├── coordinate_systems.md
        ├── feedforward_networks.md
        ├── fitness.md
        ├── floating_point_and_trigonometry.md
        ├── genetic_algorithms.md
        ├── neuroevolution.md
        ├── raycasting.md
        ├── simulation_loop.md
        └── weights_and_biases.md
```

## Dependency Graph

```
config.py ◄─── (everything imports config)

main.py
  ├── Agent
  ├── InputController
  ├── Movement
  ├── SensorSystem
  ├── Maze
  └── DebugOverlay

Agent
  ├── Movement
  └── SensorSystem

Movement
  └── Maze (collision queries: is_walkable)

SensorSystem
  └── Maze (spatial queries: is_wall)

DebugOverlay
  └── Agent (reads state)

(Future)
NeuralNetworkBrain
  └── Network.forward()

Evolution
  ├── Genome ↔ Network
  ├── Mutation
  ├── Crossover
  ├── FitnessEvaluator (bridge between simulation and selection)
  └── Population (manages agents)
```

## Design Principles

1. **Single Responsibility** — Each class owns exactly one concern.
2. **Swappable Controllers** — All brains implement `update(agent, maze)`.
3. **Centralized Configuration** — All constants live in `config.py`.
4. **Separation of Intelligence from Physics** — The agent doesn't know
   how it decides. Something tells it to move; it delegates to Movement.
5. **Read-Only World** — The maze is never modified during simulation.
6. **Flat Genomes** — Evolution sees float arrays, not neural networks.
7. **Predictive Collision** — Check before moving, never correct after.
