import config


class RuleBasedBrain:
    """Autonomous brain that decides actions based on sensor readings.

    Implements the same update(agent, maze) contract as InputController.
    No keyboard required — the agent drives itself.
    """

    def __init__(self):
        self.turning = None  # None, 'left', or 'right'

    def update(self, agent, maze):
        readings = agent.sensors.get_readings()

        # First frame: sensors haven't updated yet
        if not readings:
            return

        left, front_left, front, front_right, right = readings

        # If currently committed to a turn, keep turning until front is clear
        if self.turning is not None:
            if front > config.BRAIN_CLEAR_THRESHOLD:
                self.turning = None  # obstacle cleared, resume normal behavior
            elif self.turning == 'left':
                agent.turn_left()
                return
            else:
                agent.turn_right()
                return

        # Normal behavior: move forward or begin a turn
        if front > config.BRAIN_FRONT_THRESHOLD:
            agent.move_forward(maze)
        else:
            # Commit to a turn direction based on diagonal sensors
            if front_left > front_right:
                self.turning = 'left'
                agent.turn_left()
            else:
                self.turning = 'right'
                agent.turn_right()
