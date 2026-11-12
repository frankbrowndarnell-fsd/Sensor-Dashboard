from collections import deque
from statistics import mean, pstdev
from typing import Deque, Dict, Optional, Tuple


class AnomalyDetector:
    """Flags readings using hard limits and a rolling z-score."""

    def __init__(self, limits: Dict[str, Tuple[float, float]],
                 window_size: int = 60, min_samples: int = 15,
                 z_threshold: float = 3.0):
        self.limits = limits
        self.window_size = window_size
        self.min_samples = min_samples
        self.z_threshold = z_threshold
        self._windows: Dict[str, Deque[float]] = {}

    def check(self, sensor: str, value: float) -> Tuple[bool, Optional[str]]:
        lo, hi = self.limits.get(sensor, (float("-inf"), float("inf")))
        if not lo <= value <= hi:
            return True, f"value {value:.1f} outside limits [{lo}, {hi}]"

        window = self._windows.setdefault(sensor, deque(maxlen=self.window_size))

        if len(window) >= self.min_samples:
            mu, sigma = mean(window), pstdev(window)
            if sigma > 1e-6:
                z = abs(value - mu) / sigma
                if z > self.z_threshold:
                    # Don't add outliers to the baseline
                    return True, f"z-score {z:.1f} exceeds {self.z_threshold}"

        window.append(value)
        return False, None
