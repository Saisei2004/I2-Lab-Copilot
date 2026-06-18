"""ストレージ抽象（Repository プロトコル）。

実装は差し替え可能:
  - memory   : インメモリ（権限不要・ローカル開発/テスト用）
  - firestore: Cloud Firestore（本番）。エミュレータも同一クライアントで動く

呼び出し側は factory.get_meeting_store() / get_feedback_store() を使い、
具象クラスに依存しない。バックエンド切替は STORAGE_BACKEND だけで完結する。
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from i2_storage.models import Feedback, Meeting, TranscriptSegment


@runtime_checkable
class MeetingStore(Protocol):
    def create(self, meeting: Meeting) -> None: ...
    def get(self, meeting_id: str) -> Meeting | None: ...
    def update_status(self, meeting_id: str, status: str) -> None: ...
    def add_transcript(self, meeting_id: str, segments: list[TranscriptSegment]) -> None: ...


@runtime_checkable
class FeedbackStore(Protocol):
    def create(self, feedback: Feedback) -> None: ...
    def mark_delivered(self, feedback_id: str, delivered_at_iso: str) -> None: ...
