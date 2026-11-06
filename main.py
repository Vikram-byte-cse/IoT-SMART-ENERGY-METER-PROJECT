import os
import hmac
from pathlib import Path
import sqlite3
import time
from contextlib import contextmanager
from typing import Iterator
from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

APP_TITLE = "Smart Energy Meter API"
DB_PATH = os.getenv("DATABASE_PATH", "smart_meter.db")
DEVICE_API_KEY = os.getenv("DEVICE_API_KEY", "")
CORS_ORIGINS = [x.strip() for x in os.getenv("CORS_ORIGINS", "*").split(",") if x.strip()]

app = FastAPI(title=APP_TITLE, version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-Device-Key"],
)

class Reading(BaseModel):
    v: float = Field(ge=0, le=1000)
    i: float = Field(ge=0, le=500)
    p: float = Field(ge=-100000, le=100000)
    va: float = Field(ge=0, le=100000)
    var: float = Field(ge=-100000, le=100000)
    pf: float = Field(ge=-1, le=1)
    f: float = Field(ge=0, le=1000)
    cf: float = Field(ge=0, le=100)
    kwh: float = Field(ge=0)
    d_kwh: float = Field(ge=0)
    hr_rate: float = Field(ge=0)
    d_cost: float = Field(ge=0)
    bill: float = Field(ge=0)
    proj: float = Field(ge=0)
    co2: float = Field(ge=0)
    trees: float = Field(ge=0)
    peak_p: float = Field(ge=0)
    peak_i: float = Field(ge=0)
    grid: str = Field(default="UNKNOWN", max_length=40)
    status: str = Field(default="UNKNOWN", max_length=80)
    relay: bool = False
    uptime: str = Field(default="", max_length=40)

@contextmanager
def db() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(DB_PATH, timeout=15)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db() -> None:
    Path(DB_PATH).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
    with db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            received_at INTEGER NOT NULL,
            v REAL NOT NULL, i REAL NOT NULL, p REAL NOT NULL,
            va REAL NOT NULL, var REAL NOT NULL, pf REAL NOT NULL,
            f REAL NOT NULL, cf REAL NOT NULL, kwh REAL NOT NULL,
            d_kwh REAL NOT NULL, hr_rate REAL NOT NULL, d_cost REAL NOT NULL,
            bill REAL NOT NULL, proj REAL NOT NULL, co2 REAL NOT NULL,
            trees REAL NOT NULL, peak_p REAL NOT NULL, peak_i REAL NOT NULL,
            grid TEXT NOT NULL, status TEXT NOT NULL, relay INTEGER NOT NULL,
            uptime TEXT NOT NULL
        )""")

@app.on_event("startup")
def startup() -> None:
    init_db()

def row_to_dict(row: sqlite3.Row) -> dict:
    item = dict(row)
    item["relay"] = bool(item["relay"])
    item["connected"] = True
    return item

@app.get("/health")
def health():
    return {"status": "ok", "service": APP_TITLE, "storage": "sqlite", "device_key_configured": bool(DEVICE_API_KEY)}

@app.post("/api/readings")
def receive_reading(reading: Reading, x_device_key: str | None = Header(default=None)):
    if not DEVICE_API_KEY:
        raise HTTPException(status_code=503, detail="Server device key is not configured")
    if not x_device_key or not hmac.compare_digest(x_device_key, DEVICE_API_KEY):
        raise HTTPException(status_code=401, detail="Invalid device key")
    data = reading.model_dump()
    received_at = int(time.time())
    fields = list(data.keys())
    values = [int(data[k]) if k == "relay" else data[k] for k in fields]
    with db() as conn:
        cur = conn.execute(
            f"INSERT INTO readings (received_at,{','.join(fields)}) VALUES ({','.join(['?'] * (len(fields)+1))})",
            [received_at, *values],
        )
        reading_id = cur.lastrowid
    return {"ok": True, "id": reading_id, "received_at": received_at}

@app.get("/api/readings/latest")
def get_latest():
    with db() as conn:
        row = conn.execute("SELECT * FROM readings ORDER BY id DESC LIMIT 1").fetchone()
    if row is None:
        return {"connected": False, "message": "Waiting for the ESP32 to send its first reading."}
    result = row_to_dict(row)
    # Mark stale devices as disconnected after 30 seconds without a fresh reading.
    if int(time.time()) - result["received_at"] > 30:
        result["connected"] = False
        result["message"] = "No fresh ESP32 reading received in the last 30 seconds."
    return result

@app.get("/api/readings/history")
def get_history(limit: int = Query(default=60, ge=1, le=500)):
    with db() as conn:
        rows = conn.execute("SELECT * FROM readings ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return {"items": [row_to_dict(r) for r in reversed(rows)]}
