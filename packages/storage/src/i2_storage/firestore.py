"""Firestore リポジトリ。会議・トランスクリプト・フィードバックの CRUD。

NOTE: 初期スケルトン。クエリ最適化やトランザクションは Issue で順次対応。
"""

from __future__ import annotations

from functools import lru_cache

from google.cloud import firestore

from i2_core.config import settings
from i2_storage.models import Feedback, Meeting, TranscriptSegment


@lru_cache
def _db() -> firestore.Client:
    return firestore.Client(project=settings.google_cloud_project)


class MeetingRepository:
    COLLECTION = "meetings"

    def create(self, meeting: Meeting) -> None:
        _db().collection(self.COLLECTION).document(meeting.meeting_id).set(
            meeting.model_dump(mode="json")
        )

    def get(self, meeting_id: str) -> Meeting | None:
        snap = _db().collection(self.COLLECTION).document(meeting_id).get()
        return Meeting(**snap.to_dict()) if snap.exists else None

    def update_status(self, meeting_id: str, status: str) -> None:
        _db().collection(self.COLLECTION).document(meeting_id).update({"status": status})

    def add_transcript(self, meeting_id: str, segments: list[TranscriptSegment]) -> None:
        col = _db().collection(self.COLLECTION).document(meeting_id).collection("transcript")
        batch = _db().batch()
        for i, seg in enumerate(segments):
            batch.set(col.document(f"{i:05d}"), seg.model_dump(mode="json"))
        batch.commit()


class FeedbackRepository:
    COLLECTION = "feedback"

    def create(self, feedback: Feedback) -> None:
        _db().collection(self.COLLECTION).document(feedback.feedback_id).set(
            feedback.model_dump(mode="json")
        )

    def mark_delivered(self, feedback_id: str, delivered_at_iso: str) -> None:
        _db().collection(self.COLLECTION).document(feedback_id).update(
            {"delivered_at": delivered_at_iso}
        )
