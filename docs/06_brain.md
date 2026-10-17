# 06 — Brain (Controller Interface)

## 1. Purpose

The brain is the decision-making layer. It receives sensory information and
produces motor commands. It is the only module that answers the question:
"What should the agent do right now?"

But here's the critical design insight: **the game loop never depends on
the controller implementation.** A keyboard-controlled agent, a rule-based
agent, and a neural-network agent all look identical from the outside. They
all expose one method:

```
update(agent, maze)
```

This is the controller contract. Every brain implements it. The simulation
doesn't care how decisions are made — only that they are.

## 2. Responsibilities

**Owns:**
- Translating input (keyboard, rules, or neural network output) into agent
  commands (move_forward, turn_left, etc.).

**Should Never Own:**
- Physics or movement math (that's Movement's job).
- Sensor logic (that's the SensorSystem's job).
- Fitness evaluation (that's a future FitnessEvaluator's job).
- Rendering.
- Agent state (it commands the agent, it doesn't own it).

## 3. Theory

### Why a Uniform Interface?

In software engineering, this is called the **Strategy Pattern**. The
algorithm (how to decide) varies, but the interface (what to decide) stays
constant.

Without this pattern, switching from keyboard to neural network would
require rewriting main.py. With this pattern, it requires changing one line:

```
controller = InputController()      ← keyboard
controller = RuleBasedBrain()       ← rules
controller = NeuralNetworkBrain()   ← evolution
```

The game loop doesn't change. The maze doesn't change. The agent doesn't
change. Only the brain changes.

### Why the Brain Doesn't Own the Agent

The brain receives the agent as a parameter and issues commands. It doesn't
store a reference to "its" agent.

**Why?** In neuroevolution, we might want to test the same brain (genome)
on multiple agents, or swap brains between agents mid-simulation. If the
brain stored a reference to its agent, these operations would require
rewiring internal state.

By keeping the brain stateless (relative to the agent), we get maximum
flexibility.

### The Progression of Intelligence

```
Level 0: InputController     ← Human decides. Baseline.
Level 1: RuleBasedBrain      ← Hand-coded if/else. Control experiment.
Level 2: NeuralNetworkBrain  ← Evolved. The goal of the project.
```

Each level builds on the same interface. The complexity of the decision
increases, but the contract remains identical.

## 4. Data Flow

```
Input Source (keyboard / rules / neural network)
        │
        ▼
Controller.update(agent, maze)
        │
        ├── Read sensor values:  agent.sensors.get_readings()
        │
        ├── Decide action
        │       │
        │       ├── Keyboard: check pressed keys
        │       ├── Rules: if front < 0.3 then turn
        │       └── Neural: forward(readings) → outputs
        │
        ├── Issue commands
        │       ├── agent.move_forward(maze)
        │       ├── agent.turn_left()
        │       └── etc.
        │
        ▼
Agent state updated via Movement
```

## 5. Algorithm

### InputController (Current)

```
FUNCTION update(agent, maze):
    keys ← get_pressed_keys()

    IF key_W pressed:  agent.move_forward(maze)
    IF key_S pressed:  agent.move_backward(maze)
    IF key_A pressed:  agent.turn_left()
    IF key_D pressed:  agent.turn_right()
```

### RuleBasedBrain

```
FUNCTION update(agent, maze):
    readings ← agent.sensors.get_readings()
    front ← readings[2]        ← center sensor
    left  ← readings[0]
    right ← readings[4]

    IF front < 0.3:
        IF left > right:
            agent.turn_left()
        ELSE:
            agent.turn_right()
    ELSE:
        agent.move_forward(maze)
```

### NeuralNetworkBrain

```
FUNCTION update(agent, maze):
    inputs  ← agent.sensors.get_readings()     ← 6 floats: 5 wall rays + goal direction
    outputs ← network.forward(inputs)           ← 4 floats

    IF outputs[0] > 0.5:  agent.move_forward(maze)
    IF outputs[1] > 0.5:  agent.move_backward(maze)
    IF outputs[2] > 0.5:  agent.turn_left()
    IF outputs[3] > 0.5:  agent.turn_right()
```

## 6. Sequence of Operations

```
Every Frame
    │
    ▼
controller.update(agent, maze)
    │
    ├── (Read sensors if needed)
    ├── (Compute decision)
    └── (Issue movement commands)
    │
    ▼
agent.update(maze)
    │
    └── sensors.update()  ← refreshes readings for next frame
```

Note: the controller acts BEFORE the sensor update. It uses last frame's
sensor readings. The sensor update at the end of the frame prepares
readings for the next frame's decision. This introduces a deliberate
one-frame latency in the sense → think → act loop (our order is
think → act → sense). At 60 FPS, this 16ms delay is imperceptible
and keeps the update loop clean.

## 7. Design Decisions

### Strategy Pattern Over Inheritance

We could have `Agent` subclasses: `KeyboardAgent`, `AIAgent`, etc.

**Why not?** Inheritance couples the brain to the entity. You can't swap
brains at runtime. You can't have a population where some agents use
keyboards and others use neural networks. Composition (delegation) gives
us all of this for free.

### Sensors Before Brain in the Update Loop

The controller reads sensor values from the previous frame. This
introduces a one-frame delay.

**Why acceptable?** At 60 FPS, one frame = 16ms. The agent's environment
changes imperceptibly in that time. The neural network won't notice.
And this ordering keeps the update loop clean: decide → move → sense.

### No Abstract Base Class

We don't enforce the `update(agent, maze)` interface with Python's
`ABC` mechanism. It's a convention, not a compile-time constraint.

**Why?** Python is duck-typed. If a brain has `update(agent, maze)`, it
works. If it doesn't, it crashes immediately with a clear error. Adding
ABC boilerplate doesn't improve safety enough to justify the complexity.

## 8. Alternatives Considered

### Agent Owns the Brain (agent.brain.decide())

**Advantages:** Natural "the agent thinks" mental model.
**Disadvantages:** Harder to manage populations. The simulation must reach
inside each agent to access its brain. Testing brains in isolation requires
creating an agent.
**Why rejected:** The external controller pattern is our permanent
architecture. It keeps the main loop explicit (`controller.update` →
`agent.update` → `draw`) and allows brain swapping without touching the
agent class.

### Event-Based Control (Brain Publishes Events)

**Advantages:** Full decoupling. Brain says "TurnLeftEvent" and the system
responds.
**Disadvantages:** Significant infrastructure (event bus, listeners,
dispatchers). Overkill for our direct command model.
**Why rejected:** Direct method calls are simpler and sufficient.

## 9. Complexity Analysis

| Brain Type | Decision Complexity | Notes |
|-----------|-----------|-------|
| InputController | O(1) | 4 key checks |
| RuleBasedBrain | O(sensors) | Read + compare readings |
| NeuralNetworkBrain | O(weights) | Forward pass (see 07) |

The brain is typically the cheapest part of the frame until we scale to
thousands of neural network evaluations.

## 10. Interaction With Other Modules

```
Brain  ──reads──►   Agent.sensors.get_readings()
       ──commands──► Agent.move_forward(), turn_left(), etc.
                         │
                         ▼
                     Movement ──queries──► Maze
```

The brain sits at the top of the decision chain. It reads sensors, makes
decisions, and issues commands. Everything downstream (movement, collision)
is triggered by the brain's actions.

## 11. Future Improvements

- **Hybrid controller** — Keyboard override + neural network. Press a key
  to take manual control during training observation.
- **Recording controller** — Record inputs and replay them for
  demonstration or debugging.
