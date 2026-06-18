"""ストレージ backend のファクトリ。STORAGE_BACKEND で実装を選ぶ。

  STORAGE_BACKEND=memory     → InMemory*（権限不要・既定）
  STORAGE_BACKEND=firestore  → Firestore*（本番。FIRESTORE_EMULATOR_HOST 設定時はエミュレータ）

呼び出し側はこの関数だけを使い、具象に依存しない。後から backend を変えても
呼び出しコードは無改修。
"""

from __future__ import annotations

from functools import lru_cache

from i2_core.config import settings
from i2_storage.base import FeedbackStore, MeetingStore


@lru_cache
def get_meeting_store() -> MeetingStore:
    if settings.storage_backend == "firestore":
        from i2_storage.firestore import MeetingRepository

        return MeetingRepository()
    from i2_storage.memory import InMemoryMeetingStore

    return InMemoryMeetingStore()


@lru_cache
def get_feedback_store() -> FeedbackStore:
    if settings.storage_backend == "firestore":
        from i2_storage.firestore import FeedbackRepository

        return FeedbackRepository()
    from i2_storage.memory import InMemoryFeedbackStore

    return InMemoryFeedbackStore()
