"""Firestore ドキュメントの Pydantic モデル。docs/architecture.md のデータモデルに対応。"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class MeetingStatus(StrEnum):
    RECORDING = "recording"
    TRANSCRIBING = "transcribing"
    SUMMARIZING = "summarizing"
    DONE = "done"
    ERROR = "error"


class User(BaseModel):
    discord_user_id: str
    display_name: str
    github_username: str | None = None
    report_branch: str | None = None  # progress2026 上の各自ブランチ
    created_at: datetime | None = None


class TranscriptSegment(BaseModel):
    speaker_id: str  # discord_user_id（per-user sink で確定）
    start_ms: int
    end_ms: int
    text: str


class ActionItem(BaseModel):
    assignee: str | None = None
    text: str
    due: str | None = None


class MeetingSummary(BaseModel):
    topics: list[str] = Field(default_factory=list)
    decisions: list[str] = Field(default_factory=list)
    action_items: list[ActionItem] = Field(default_factory=list)
    raw: str = ""


class Meeting(BaseModel):
    meeting_id: str
    guild_id: str
    channel_id: str
    started_at: datetime | None = None
    ended_at: datetime | None = None
    participants: list[str] = Field(default_factory=list)
    gcs_audio_prefix: str | None = None
    status: MeetingStatus = MeetingStatus.RECORDING
    summary: MeetingSummary | None = None


class Feedback(BaseModel):
    feedback_id: str
    meeting_id: str
    target_user_id: str
    source: str  # "meeting" | "ai"
    text: str
    created_at: datetime | None = None
    delivered_at: datetime | None = None
