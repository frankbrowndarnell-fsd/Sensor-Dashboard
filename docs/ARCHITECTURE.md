# Architecture

## Overview

```
┌────────────┐   Reading    ┌──────────────────┐   flagged    ┌────────────┐
│ Simulator  │ ───────────▶ │ AnomalyDetector  │ ───────────▶ │ Broadcast  │
│ (or real)  │              │ (per-sensor      │   Reading    │ hub (set   │
└────────────┘              │  rolling window) │              │ of WS      │
                            └──────────────────┘              │ clients)   │
                                                              └─────┬──────┘
                                                                    │ JSON
                                                              ┌─────▼──────┐
                                                              │  Browser   │
                                                              │  dashboard │
                                                              └────────────┘
```

## Components

### Producer (`main.py`)
An asyncio background task started at app startup. Every `TICK_SECONDS` it asks the simulator for one reading per sensor, passes each through the detector, stores the result in a `latest` dict, and pushes it to all connected WebSocket clients.

### Simulator (`simulator.py`)
Generates smooth signals (sine wave + Gaussian noise) per sensor. With probability `SPIKE_PROBABILITY` it injects a large offset so the detector has something to find.

### Anomaly detector (`anomaly.py`)
Two checks per reading:
1. **Hard limits**: configured min/max per sensor (e.g. humidity must be 0–100%).
2. **Rolling z-score**: maintains a deque of recent values; flags if `|value - mean| / std > Z_THRESHOLD`. Skipped until `MIN_SAMPLES` collected or when `std` is ~0.

Anomalous values are **not** added to the window, so a burst of bad readings doesn't distort the baseline.

### Frontend (`frontend/`)
Static files served by FastAPI. `app.js` opens a WebSocket, updates one card per sensor, and appends points to a rolling Chart.js line chart. Anomalous points are highlighted in red and listed in an event log.

## Design Decisions

| Decision | Rationale | Trade-off |
|----------|-----------|-----------|
| WebSocket over polling | Low latency, less overhead | Needs sticky sessions if scaled out |
| In-memory state | Simplest possible prototype | No history, no multi-worker |
| Z-score + hard limits | Easy to explain and test | Weak against drift/seasonality |
| Static frontend, no build step | Zero tooling to start | Less structure for larger UIs |

## Scaling Path

1. Add a message broker (Redis pub/sub or MQTT) between producers and WebSocket servers.
2. Persist readings in a time-series DB.
3. Move detection into a separate worker/service.
4. Add auth and per-device keys.
