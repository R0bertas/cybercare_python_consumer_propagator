# Event Propagator / Consumer

Two small Python services:

- `consumer`: FastAPI service exposing `POST /event` that persists incoming events to `events.db` (SQLite).
- `propagator`: Periodically reads `events.json` and sends a random event to the consumer endpoint.

## Configuration

Both services read from `config.json` by default. CLI arguments override config file values.


## Quick Start

1. Install Poetry: https://python-poetry.org/docs/
2. From the `event_services` folder:

```bash
poetry install
make run-consumer
```

In another terminal:

```bash
make run-propagator
```

## Endpoints

- `GET /` - Health check
- `POST /event` - Accept an event or array of events
- `GET /events` - List all stored events

## Database

View stored events:
```bash
make show-db
# or
sqlite3 events.db "SELECT * FROM events;"
```

## Run Tests
```bash
poetry run pytest tests/ -v
```

## To see better logging run in terminal while consumer is running

```bash

curl -X POST http://127.0.0.1:8000/event \
  -H "Content-Type: application/json" \
  -d '{"invalid": "data"}' \
  -v
```


Possible future Upates:
- Better logging 
- Using different database  
- Paggination for endpoints 
- Different endpoints like delete from database, search in database 
- Support for CLI comamnds ( in task it was as OR , so optional) 
- More tests 