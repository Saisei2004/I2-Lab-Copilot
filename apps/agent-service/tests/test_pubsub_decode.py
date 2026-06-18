import base64
import json

from i2_agent_service.main import _decode_pubsub
from i2_agent_service.pipeline import RecordingEvent


def test_decode_pubsub_roundtrip():
    payload = {"meeting_id": "g-1", "speakers": ["1", "2"]}
    data = base64.b64encode(json.dumps(payload).encode()).decode()
    assert _decode_pubsub({"message": {"data": data}}) == payload


def test_decode_pubsub_empty():
    assert _decode_pubsub({"message": {}}) == {}


def test_recording_event_parse():
    ev = RecordingEvent(
        meeting_id="g-1",
        guild_id="g",
        channel_id="c",
        gcs_prefix="g-1",
        speakers=["1", "2"],
    )
    assert ev.speakers == ["1", "2"]
