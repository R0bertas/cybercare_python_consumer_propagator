import json
import os
import sys
from unittest.mock import patch
from fastapi.testclient import TestClient
from consumer import main as cm
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_root_endpoint():
    client = TestClient(cm.app)
    response = client.get("/")
    
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["message"] == "Event Consumer is running"


def test_init_db_creates_table(tmp_path):
    test_db = tmp_path / "test.db"
    
    cm.init_db(path=test_db)
    
    assert test_db.exists()
    
    import sqlite3
    conn = sqlite3.connect(test_db)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='events'")
    result = cur.fetchone()
    conn.close()
    
    assert result is not None
    assert result[0] == "events"


def test_persist_event(tmp_path, monkeypatch):
    test_db = tmp_path / "test.db"
    monkeypatch.setattr(cm, "DB_PATH", test_db)
    
    cm.init_db(path=test_db)
    
    event = {"event_type": "user.login", "event_payload": "user123"}
    cm.persist_event(event)
    
    import sqlite3
    conn = sqlite3.connect(test_db)
    cur = conn.cursor()
    cur.execute("SELECT event_type, event_payload FROM events")
    row = cur.fetchone()
    conn.close()
    
    assert row is not None
    assert row[0] == "user.login"
    assert json.loads(row[1]) == "user123"


def test_post_single_event(tmp_path, monkeypatch):
    """Test posting a single event to /event endpoint"""
    test_db = tmp_path / "test.db"
    monkeypatch.setattr(cm, "DB_PATH", test_db)
    cm.init_db(path=test_db)
    
    client = TestClient(cm.app)
    
    payload = {"event_type": "test.event", "event_payload": "test data"}
    response = client.post("/event", json=payload)
    
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["received"] == 1


def test_post_multiple_events(tmp_path, monkeypatch):
    test_db = tmp_path / "test.db"
    monkeypatch.setattr(cm, "DB_PATH", test_db)
    cm.init_db(path=test_db)
    
    client = TestClient(cm.app)
    
    payload = [
        {"event_type": "event1", "event_payload": "data1"},
        {"event_type": "event2", "event_payload": "data2"}
    ]
    response = client.post("/event", json=payload)
    
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["received"] == 2


def test_get_all_events(tmp_path, monkeypatch):
    test_db = tmp_path / "test.db"
    monkeypatch.setattr(cm, "DB_PATH", test_db)
    cm.init_db(path=test_db)
    
    client = TestClient(cm.app)
    
    client.post("/event", json={"event_type": "event1", "event_payload": "data1"})
    client.post("/event", json={"event_type": "event2", "event_payload": "data2"})
    
    response = client.get("/events")
    
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert len(body["events"]) == 2
    assert body["events"][0]["event_type"] == "event1"
    assert body["events"][1]["event_type"] == "event2"


def test_post_event_missing_fields():
    client = TestClient(cm.app)
    
    response = client.post("/event", json={"foo": "bar"})
    
    assert response.status_code == 400
    assert "Missing event_type or event_payload" in response.json()["detail"]


def test_post_event_wrong_type_for_event_type():
    client = TestClient(cm.app)
    
    response = client.post("/event", json={"event_type": 123, "event_payload": "data"})
    
    assert response.status_code == 400
    assert "must be strings" in response.json()["detail"]


def test_post_event_wrong_type_for_event_payload():
    client = TestClient(cm.app)
    
    response = client.post("/event", json={"event_type": "test", "event_payload": {"key": "value"}})
    
    assert response.status_code == 400
    assert "must be strings" in response.json()["detail"]


def test_post_event_invalid_payload_type():
    client = TestClient(cm.app)
    
    response = client.post("/event", json="invalid")
    
    assert response.status_code == 400
    assert "must be an object or array" in response.json()["detail"]


def test_post_event_array_with_invalid_item():
    client = TestClient(cm.app)
    
    response = client.post("/event", json=[
        {"event_type": "test", "event_payload": "data"},
        "invalid item"
    ])
    
    assert response.status_code == 400
    assert "must be an object" in response.json()["detail"]


def test_main_starts_server(monkeypatch):
    with patch("uvicorn.run") as mock_run:
        cm.main()
        
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert call_args[0][0] == cm.app
        assert call_args[1]["host"] == cm.HOST
        assert call_args[1]["port"] == cm.PORT


def test_get_events_empty_database(tmp_path, monkeypatch):
    test_db = tmp_path / "test.db"
    monkeypatch.setattr(cm, "DB_PATH", test_db)
    cm.init_db(path=test_db)
    
    client = TestClient(cm.app)
    response = client.get("/events")
    
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["events"] == []