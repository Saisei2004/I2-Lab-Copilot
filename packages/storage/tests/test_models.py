from i2_integrations.transcription import merge_tracks
from i2_storage.models import Meeting, MeetingStatus, TranscriptSegment


def test_meeting_defaults():
    m = Meeting(meeting_id="m1", guild_id="g1", channel_id="c1")
    assert m.status is MeetingStatus.RECORDING
    assert m.participants == []


def test_merge_tracks_sorts_by_start():
    a = [TranscriptSegment(speaker_id="u1", start_ms=300, end_ms=400, text="b")]
    b = [TranscriptSegment(speaker_id="u2", start_ms=100, end_ms=200, text="a")]
    merged = merge_tracks({"u1": a, "u2": b})
    assert [s.text for s in merged] == ["a", "b"]
