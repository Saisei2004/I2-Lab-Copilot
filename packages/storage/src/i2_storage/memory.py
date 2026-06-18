"""インメモリ実装。GCP 権限なしでローカル開発・テストを回すための backend。

プロセス内辞書に保持するため再起動で消える（開発用途のみ）。
本番は firestore backend を使う。
"""

from __future__ import annotations

from i2_storage.models import Feedback, Meeting, TranscriptSegment


class InMemoryMeetingStore:
    def __init__(self) -> None:
        self._meetings: dict[str, Meeting] = {}
        self._transcripts: dict[str, list[TranscriptSegment]] = {}

    def create(self, meeting: Meeting) -> None:
        self._meetings[meeting.meeting_id] = meeting

    def get(self, meeting_id: str) -> Meeting | None:
        return self._meetings.get(meeting_id)

    def update_status(self, meeting_id: str, status: str) -> None:
        m = self._meetings.get(meeting_id)
        if m:
            m.status = status  # type: ignore[assignment]

    def add_transcript(self, meeting_id: str, segments: list[TranscriptSegment]) -> None:
        self._transcripts.setdefault(meeting_id, []).extend(segments)

    def transcript(self, meeting_id: str) -> list[TranscriptSegment]:
        return self._transcripts.get(meeting_id, [])


class InMemoryFeedbackStore:
    def __init__(self) -> None:
        self._feedback: dict[str, Feedback] = {}

    def create(self, feedback: Feedback) -> None:
        self._feedback[feedback.feedback_id] = feedback

    def mark_delivered(self, feedback_id: str, delivered_at_iso: str) -> None:
        fb = self._feedback.get(feedback_id)
        if fb:
            fb.delivered_at = delivered_at_iso  # type: ignore[assignment]
