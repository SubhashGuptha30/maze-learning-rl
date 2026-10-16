import math


def sigmoid(x):
    """Squashes any value into the range (0, 1).

    sigmoid(-∞) → 0
    sigmoid(0)  → 0.5
    sigmoid(+∞) → 1

    Used as the default activation because outputs naturally
    map to thresholds (> 0.5 = execute command).
    """
    # Clamp to prevent math overflow on extreme values
    x = max(-500, min(500, x))
    return 1.0 / (1.0 + math.exp(-x))
