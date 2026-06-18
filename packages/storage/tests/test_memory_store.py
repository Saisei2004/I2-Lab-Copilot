from i2_storage.base import FeedbackStore, MeetingStore
from i2_storage.memory import InMemoryFeedbackStore, InMemoryMeetingStore
from i2_storage.models import Feedback, Meeting, MeetingStatus, TranscriptSegment


def test_memory_meeting_roundtrip():
    store = InMemoryMeetingStore()
    assert isinstance(store, MeetingStore)  # プロトコル適合
    store.create(Meeting(meeting_id="m1", guild_id="g", channel_id="c"))
    store.update_status("m1", MeetingStatus.DONE.value)
    store.add_transcript(
        "m1", [TranscriptSegment(speaker_id="u1", start_ms=0, end_ms=1, text="hi")]
    )

    got = store.get("m1")
    assert got is not None
    assert got.status == MeetingStatus.DONE
    assert store.transcript("m1")[0].text == "hi"


def test_memory_feedback_delivered():
    store = InMemoryFeedbackStore()
    assert isinstance(store, FeedbackStore)
    store.create(
        Feedback(feedback_id="f1", meeting_id="m1", target_user_id="u1", source="ai", text="x")
    )
    store.mark_delivered("f1", "2026-06-18T00:00:00Z")
    assert store._feedback["f1"].delivered_at == "2026-06-18T00:00:00Z"
