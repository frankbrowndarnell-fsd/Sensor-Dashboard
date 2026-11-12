import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    tick_seconds: float = float(os.getenv("TICK_SECONDS", "1.0"))
    window_size: int = int(os.getenv("WINDOW_SIZE", "60"))
    min_samples: int = int(os.getenv("MIN_SAMPLES", "15"))
    z_threshold: float = float(os.getenv("Z_THRESHOLD", "3.0"))
    spike_probability: float = float(os.getenv("SPIKE_PROBABILITY", "0.02"))


settings = Settings()

# name -> (unit, hard_min, hard_max)
SENSORS = {
    "temperature": ("°C", -20.0, 60.0),
    "humidity": ("%", 0.0, 100.0),
    "light": ("lux", 0.0, 10000.0),
}
