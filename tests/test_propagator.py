import json
import os
import sys
from unittest.mock import Mock, patch
import pytest
from propagator import main as pm

# here for module import 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_load_events_from_file(tmp_path):
    events_file = tmp_path / "events.json"
    test_events = [
        {"event_type": "user.login", "event_payload": "user123"},
        {"event_type": "user.logout", "event_payload": "user456"}
    ]
    events_file.write_text(json.dumps(test_events))
    
    events = pm.load_events(str(events_file))
    
    assert len(events) == 2
    assert events[0]["event_type"] == "user.login"
    assert events[1]["event_type"] == "user.logout"


def test_load_events_file_does_not_exist():
    with pytest.raises(FileNotFoundError):
        pm.load_events("this_file_does_not_exist.json")


def test_load_events_invalid_json(tmp_path):
    events_file = tmp_path / "bad.json"
    events_file.write_text("this is not valid json")
    
    with pytest.raises(json.JSONDecodeError):
        pm.load_events(str(events_file))


async def test_send_loop_posts_events():
    fake_response = Mock()
    fake_response.status_code = 200
    
    fake_client = Mock()
    fake_client.post = Mock(return_value=fake_response)
    
    events = [{"event_type": "test", "event_payload": "data"}]
    
    with patch("httpx.AsyncClient") as MockClient:
        MockClient.return_value.__aenter__.return_value = fake_client
        
        with patch("asyncio.sleep", side_effect=KeyboardInterrupt):
            try:
                await pm.send_loop("http://example.com/event", events, 1.0)
            except KeyboardInterrupt:
                pass
    
    fake_client.post.assert_called_once()
    assert fake_client.post.call_args[0][0] == "http://example.com/event"


async def test_send_loop_continues_on_error():
    fake_client = Mock()
    fake_client.post = Mock(side_effect=Exception("Network error"))
    
    events = [{"event_type": "test", "event_payload": "data"}]
    
    with patch("httpx.AsyncClient") as MockClient:
        MockClient.return_value.__aenter__.return_value = fake_client
        
        with patch("asyncio.sleep", side_effect=KeyboardInterrupt):
            try:
                await pm.send_loop("http://example.com/event", events, 1.0)
            except KeyboardInterrupt:
                pass
    
    fake_client.post.assert_called_once()


def test_main_with_valid_config(tmp_path):
    events_file = tmp_path / "events.json"
    events_file.write_text(json.dumps([{"event_type": "test", "event_payload": "data"}]))
    
    fake_config = {
        "url": "http://example.com/event",
        "interval": 1.0,
        "events_file_path": str(events_file)
    }
    
    with patch("propagator.main.load_propagator", return_value=fake_config):
        with patch("asyncio.run", side_effect=KeyboardInterrupt) as mock_run:
            pm.main()
            
            mock_run.assert_called_once()


def test_main_stops_if_events_file_missing():
    fake_config = {
        "url": "http://example.com/event",
        "interval": 1.0,
        "events_file_path": "missing_file.json"
    }
    
    with patch("propagator.main.load_propagator", return_value=fake_config):
        with patch("asyncio.run") as mock_run:
            pm.main()
            
            # asyncio.run should NOT be called because events file is missing
            mock_run.assert_not_called()


def test_main_uses_default_values(tmp_path):
    events_file = tmp_path / "events.json"
    events_file.write_text(json.dumps([{"event_type": "test", "event_payload": "data"}]))
    
    fake_config = {
        "events_file_path": str(events_file)
    }
    
    with patch("propagator.main.load_propagator", return_value=fake_config):
        with patch("asyncio.run", side_effect=KeyboardInterrupt) as mock_run:
            pm.main()
            
            mock_run.assert_called_once()