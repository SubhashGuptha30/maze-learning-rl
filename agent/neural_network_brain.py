class NeuralNetworkBrain:
    """Brain that delegates decisions to a neural network.

    Implements the same update(agent, maze) contract as InputController
    and RuleBasedBrain. The brain doesn't know how the network works —
    it simply asks for outputs and translates them into movement commands.
    """

    def __init__(self, network):
        self.network = network

    def update(self, agent, maze):
        """Act for one frame. Returns how many moves a wall rejected (0-2)."""
        readings = agent.sensors.get_readings()

        # First frame: sensors haven't updated yet
        if not readings:
            return 0

        outputs = self.network.forward(readings)

        # Each output independently controls one action
        blocked = 0
        if outputs[0] > 0.5:
            blocked += not agent.move_forward(maze)
        if outputs[1] > 0.5:
            blocked += not agent.move_backward(maze)
        if outputs[2] > 0.5:
            agent.turn_left()
        if outputs[3] > 0.5:
            agent.turn_right()

        return blocked
