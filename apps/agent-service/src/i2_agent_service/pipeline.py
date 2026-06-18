"""録音完了 → 文字起こし → 要約 → 個人FB のパイプライン本体。

Pub/Sub `recording-done` を受けて実行される。GCP 認証・Vertex AI・STT が必要なため
ローカルでは各 I/O をモックして単体検証する（test_pipeline 参照）。
"""

from __future__ import annotations

import asyncio

from pydantic import BaseModel

from i2_agents.agent import feedback_agent, meeting_agent
from i2_agents.runner import run_agent_text
from i2_core.clock import iso_now, utcnow
from i2_core.config import settings
from i2_core.ids import new_feedback_id
from i2_core.logging import get_logger
from i2_integrations import discord_rest
from i2_integrations.transcription import (
    merge_tracks,
    transcribe_track,
    transcript_to_text,
)
from i2_storage.firestore import FeedbackRepository, MeetingRepository
from i2_storage.models import Feedback, MeetingStatus

log = get_logger("i2_agent_service.pipeline")


class RecordingEvent(BaseModel):
    meeting_id: str
    guild_id: str
    channel_id: str
    gcs_prefix: str
    speakers: list[str]


def _gcs_uri(prefix: str, speaker_id: str) -> str:
    return f"gs://{settings.gcs_bucket_recordings}/{prefix}/{speaker_id}.wav"


async def run_pipeline(event: RecordingEvent) -> None:
    meetings = MeetingRepository()
    feedbacks = FeedbackRepository()
    log.info("pipeline_start", meeting_id=event.meeting_id, speakers=event.speakers)

    # 1. 文字起こし（話者ごと）→ マージ
    per_speaker = {}
    for uid in event.speakers:
        per_speaker[uid] = await asyncio.to_thread(
            transcribe_track, _gcs_uri(event.gcs_prefix, uid), uid
        )
    segments = merge_tracks(per_speaker)
    transcript_text = transcript_to_text(segments)
    await asyncio.to_thread(meetings.add_transcript, event.meeting_id, segments)
    await asyncio.to_thread(
        meetings.update_status, event.meeting_id, MeetingStatus.SUMMARIZING.value
    )

    # 2. 会議要約 → 要約チャンネル（未設定なら会議チャンネル）へ投稿
    summary = await run_agent_text(
        meeting_agent, f"以下は会議の発話ログです。要約してください。\n\n{transcript_text}"
    )
    target_channel = settings.discord_summary_channel_id or int(event.channel_id)
    await asyncio.to_thread(
        discord_rest.post_message, target_channel, f"📝 **会議要約**\n{summary}"
    )

    # 3. 個人フィードバック → 各人へ DM
    for uid in event.speakers:
        fb_text = await run_agent_text(
            feedback_agent,
            f"対象メンバーの discord_user_id={uid}。以下の発話ログを踏まえ、"
            f"この人に向けた会議フィードバックと AI からの助言を作成してください。\n\n{transcript_text}",
        )
        await asyncio.to_thread(
            discord_rest.send_dm, int(uid), f"💬 **会議フィードバック**\n{fb_text}"
        )
        await asyncio.to_thread(
            feedbacks.create,
            Feedback(
                feedback_id=new_feedback_id(),
                meeting_id=event.meeting_id,
                target_user_id=uid,
                source="ai",
                text=fb_text,
                created_at=utcnow(),
                delivered_at=None,
            ),
        )

    await asyncio.to_thread(meetings.update_status, event.meeting_id, MeetingStatus.DONE.value)
    log.info("pipeline_done", meeting_id=event.meeting_id, at=iso_now())
