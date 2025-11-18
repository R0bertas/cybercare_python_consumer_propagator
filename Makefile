PY=python3

.PHONY: install run-consumer run-propagator show-db help

help:
	@echo "Event Propagator / Consumer - Available commands:"
	@echo "  make install           - Install dependencies via Poetry"
	@echo "  make run-consumer      - Run consumer service (uses config.json)"
	@echo "  make run-propagator    - Run propagator service (uses config.json)"
	@echo "  make show-db           - Show last 20 events in database"

install:
	poetry install

run-consumer:
	poetry run $(PY) consumer/main.py 

run-propagator:
	poetry run $(PY) propagator/main.py

show-db:
	sqlite3 events.db "SELECT id,event_type,event_payload,received_at FROM events ORDER BY id DESC LIMIT 20;"
