import asyncio
import json
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

from . import simulator
from .anomaly import AnomalyDetector
from .config import SENSORS, settings

clients: Set[WebSocket] = set()
latest: Dict[str, dict] = {}
detector = AnomalyDetector(
    limits={k: (v[1], v[2]) for k, v in SENSORS.items()},
    window_size=settings.window_size,
    min_samples=settings.min_samples,
    z_threshold=settings.z_threshold,
)


async def broadcast(message: dict) -> None:
    payload = json.dumps(message)
    dead = []
    for ws in clients:
        try:
            await ws.send_text(payload)
        except Exception:
            dead.append(ws)
    for ws in dead:
        clients.discard(ws)


async def producer() -> None:
    while True:
        for sensor, value in simulator.read_all().items():
            anomaly, reason = detector.check(sensor, value)
            reading = {
                "sensor": sensor,
                "value": value,
                "unit": SENSORS[sensor][0],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "anomaly": anomaly,
                "reason": reason,
            }
            latest[sensor] = reading
            await broadcast(reading)
        await asyncio.sleep(settings.tick_seconds)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(producer())
    yield
    task.cancel()


app = FastAPI(title="SensorPulse", lifespan=lifespan)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/latest")
def get_latest():
    return latest


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    clients.add(ws)
    try:
        while True:
            await ws.receive_text()  # keep connection open
    except WebSocketDisconnect:
        clients.discard(ws)


FRONTEND = Path(__file__).resolve().parents[2] / "frontend"
app.mount("/", StaticFiles(directory=FRONTEND, html=True), name="frontend")
