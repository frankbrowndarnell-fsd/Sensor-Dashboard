🌡️ SensorPulse
A real-time sensor dashboard for temperature, humidity, and light readings, with automatic anomaly flagging.
![status](https://img.shields.io/badge/status-prototype-orange)
![python](https://img.shields.io/badge/python-3.10%2B-blue)
![license](https://img.shields.io/badge/license-MIT-green)
> **Note:** This is a starter/prototype project. It ships with a built-in sensor simulator so you can see the full pipeline without any hardware.
---
Features
Live streaming of readings over WebSocket (1 reading per sensor per second by default)
Live line chart and status cards for each sensor
Anomaly flagging using two complementary methods:
Hard limits: values outside a physically sensible range
Rolling z-score: values that deviate sharply from recent history
Built-in simulator with randomly injected spikes for demo/testing
Docker support and a CI workflow
Screenshot
Add a screenshot here once you've run it: `docs/screenshot.png`
Tech Stack
Layer	Choice
Backend	Python 3.10+, FastAPI, Uvicorn
Transport	WebSocket (`/ws`) + REST
Frontend	Vanilla JS, Chart.js (via CDN)
Testing	pytest
Packaging	Docker / docker-compose
Project Structure
```
sensor-dashboard/
├── backend/app/
│   ├── main.py          # FastAPI app, WebSocket broadcast, background producer
│   ├── simulator.py     # Fake sensor data generator
│   ├── anomaly.py       # Anomaly detection logic
│   └── config.py        # Env-based settings
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── style.css
├── tests/
│   └── test_anomaly.py
├── docs/
│   └── ARCHITECTURE.md
├── .github/workflows/ci.yml
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```
Setup
Prerequisites
Python 3.10 or newer
(Optional) Docker 24+
Option A: Local
```bash
git clone https://github.com/<your-username>/sensor-dashboard.git
cd sensor-dashboard

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env             # optional: tweak settings
uvicorn backend.app.main:app --reload
```
Open http://localhost:8000.
Option B: Docker
```bash
docker compose up --build
```
Open http://localhost:8000.
Run the tests
```bash
pytest -q
```
Configuration
Set via environment variables or a `.env` file (see `.env.example`).
Variable	Default	Description
`TICK_SECONDS`	`1.0`	Seconds between readings
`WINDOW_SIZE`	`60`	Samples kept for rolling statistics
`MIN_SAMPLES`	`15`	Samples needed before z-score checks begin
`Z_THRESHOLD`	`3.0`	Z-score above which a reading is flagged
`SPIKE_PROBABILITY`	`0.02`	Chance per reading that the simulator injects a spike
API
Endpoint	Description
`GET /api/health`	Liveness check
`GET /api/latest`	Latest reading for each sensor
`WS  /ws`	Live stream of readings
Example WebSocket message:
```json
{
  "sensor": "temperature",
  "value": 41.7,
  "unit": "°C",
  "timestamp": "2026-11-12T10:15:03.120Z",
  "anomaly": true,
  "reason": "z-score 4.2 exceeds 3.0"
}
```
Architecture (summary)
```
[Simulator / real sensors] -> [Anomaly detector] -> [Broadcast hub] -> WebSocket -> [Browser dashboard]
```
See docs/ARCHITECTURE.md for details and design decisions.
Connecting Real Sensors
Replace the simulator in `backend/app/main.py` with a source that yields the same `Reading` dict shape. Options include an MQTT subscriber, a serial reader (e.g. Arduino/ESP32), or an HTTP ingest endpoint. Keep the detector call unchanged.
Known Limitations
No persistence. Readings live in memory only; a restart loses history.
Simulated data only out of the box. No hardware drivers are included.
Single process. Broadcasting uses an in-memory client set, so running multiple workers will split clients and state.
Simple detection. Z-score on a rolling window can miss slow drift and may flag legitimate rapid changes (e.g. a light turning on). It does not model seasonality or sensor correlation.
Cold start. No z-score flagging until `MIN_SAMPLES` is reached (hard limits still apply).
No authentication or TLS. Do not expose it to the public internet as-is.
Frontend depends on a CDN for Chart.js, so the UI needs internet access unless you vendor the library.
No alerting. Anomalies are shown in the UI only (no email, SMS, or webhook).
Limited test coverage. Only the anomaly logic is tested.
Roadmap
[ ] Time-series storage (SQLite, then TimescaleDB/InfluxDB)
[ ] MQTT ingest
[ ] Alerting (email/webhook)
[ ] Historical view and CSV export
[ ] Auth and per-device API keys
[ ] Smarter detection (EWMA, seasonal decomposition)
Contributing
See CONTRIBUTING.md.
License
MIT, see LICENSE.
