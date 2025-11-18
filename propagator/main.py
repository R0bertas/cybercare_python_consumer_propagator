import asyncio
import json
import random
import time
from typing import Any, List
import httpx
from utils.utils import load_propagator


def load_events(path: str) -> List[Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


async def send_loop(url: str, events: List[Any], interval: float):
    async with httpx.AsyncClient(timeout=10.0) as client:
        while True:
            event = random.choice(events)
            try:
                r = await client.post(url, json=event)
                print(f"[{time.strftime('%H:%M:%S')}] Sent event -> status={r.status_code}")
            except Exception as e:
                print(f"Error sending event: {e}")
            await asyncio.sleep(interval)


def main():
    config = load_propagator()
    url = config.get("url", "http://127.0.0.1:8000/event")
    interval = config.get("interval", 5.0)
    events_file = config.get("events_file_path", "events.json")

    try:
        events = load_events(events_file)
    except Exception as e:
        print(f"Failed to load events from {events_file}: {e}")
        return

    print(f"Starting propagator: url={url} interval={interval}s events={len(events)}")
    try:
        asyncio.run(send_loop(url, events, interval))
    except KeyboardInterrupt:
        print("Stopped by user")


if __name__ == "__main__":
    main()