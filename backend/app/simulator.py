import math
import random
import time
from typing import Dict

from .config import SENSORS, settings

# name -> (baseline, amplitude, noise, spike_size)
_PROFILE = {
    "temperature": (22.0, 3.0, 0.2, 15.0),
    "humidity": (45.0, 8.0, 0.8, 30.0),
    "light": (400.0, 150.0, 10.0, 3000.0),
}


def read_all() -> Dict[str, float]:
    """Return one simulated reading per sensor."""
    t = time.time()
    out = {}
    for name in SENSORS:
        base, amp, noise, spike = _PROFILE[name]
        value = base + amp * math.sin(t / 60.0) + random.gauss(0, noise)
        if random.random() < settings.spike_probability:
            value += random.choice([-1, 1]) * spike
        out[name] = round(value, 2)
    return out
