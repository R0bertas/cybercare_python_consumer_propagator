from datetime import datetime
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from utils.utils import load_consumer


# Load defaults from config file
_config = load_consumer()
DB_PATH = Path(_config.get("db_path", "events.db"))
DB_TYPE = _config.get("db_type", "sqlite")
HOST = _config.get("host", "127.0.0.1")
PORT = _config.get("port", 8000)

app = FastAPI(title="Event Consumer")


def init_db(path: Path = DB_PATH):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT,
            event_payload TEXT,
            received_at TEXT
        )
        """
    )
    conn.commit()
    conn.close()


@app.on_event("startup")
def startup():
    init_db()


def persist_event(event: Dict[str, Any]):
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO events (event_type, event_payload, received_at) VALUES (?, ?, ?)",
            (
                str(event.get("event_type")), 
                json.dumps(event.get("event_payload")), 
                datetime.now().isoformat()
            ),
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()


@app.get("/")
async def root():
    return {"status": "ok", "message": "Event Consumer is running"}

@app.post("/event")
async def receive_event(request: Request):
    data = await request.json()

    if isinstance(data, dict):
        items = [data]
    elif isinstance(data, list):
        items = data
    else:
        raise HTTPException(status_code=400, detail="Payload must be an object or array of objects")

    persisted = 0
    for item in items:
        if not isinstance(item, dict):
            raise HTTPException(status_code=400, detail="Each item must be an object")
        if "event_type" not in item or "event_payload" not in item:
            raise HTTPException(status_code=400, detail="Missing event_type or event_payload")
        if not isinstance(item.get("event_type"), str) or not isinstance(item.get("event_payload"), str):
            raise HTTPException(status_code=400, detail="event_type and event_payload must be strings")

        persist_event(item)
        persisted += 1

    return {"status": "ok", "received": persisted}


@app.get("/events")
async def get_all_events():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, event_type, event_payload, received_at FROM events")
    rows = cur.fetchall()
    events = []
    for row in rows:
        events.append({
            "id": row[0],
            "event_type": row[1],
            "event_payload": json.loads(row[2]),
            "received_at": row[3],
        })
    conn.close()
    return {"status": "ok", "events": events}


def main():

    print(f"Starting consumer: host={HOST} port={PORT} db_path={DB_PATH}")
    uvicorn.run(app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()
