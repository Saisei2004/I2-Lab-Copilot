"""録音（③）。py-cord の voice receive (WaveSink) で話者ごとに録音する。

フロー:
  start → VC 接続 → WaveSink で録音開始 → 同意メッセージ再通知
  stop  → 録音停止 → 話者別 WAV を GCS へ → Firestore 会議更新 → Pub/Sub(recording-done)
          → 以降は agent-service が文字起こし→要約→個人FBを担当

ブロッキングな GCP 呼び出しは asyncio.to_thread で逃がし、Gateway のハートビートを止めない。
"""

from __future__ import annotations

import asyncio
import contextlib
from dataclasses import dataclass, field

import discord

from i2_core.clock import utcnow
from i2_core.config import settings
from i2_core.ids import new_meeting_id
from i2_core.logging import get_logger
from i2_core.pubsub import publish
from i2_storage import get_meeting_store
from i2_storage.gcs import upload_bytes
from i2_storage.models import Meeting, MeetingStatus

log = get_logger("i2_bot.recording")


@dataclass
class _Session:
    meeting_id: str
    vc: discord.VoiceClient
    channel_id: int
    started_at: str
    participants: list[str] = field(default_factory=list)


class RecordingManager:
    """guild ごとの録音状態を管理する。"""

    def __init__(self) -> None:
        self._sessions: dict[int, _Session] = {}
        self._meetings = get_meeting_store()

    async def start(self, ctx: discord.ApplicationContext) -> None:
        if ctx.guild.id in self._sessions:
            await ctx.respond("既に録音中です。`/record stop` で停止してください。", ephemeral=True)
            return

        channel = ctx.author.voice.channel
        vc = await channel.connect()
        meeting_id = new_meeting_id(ctx.guild.id)
        participants = [str(m.id) for m in channel.members if not m.bot]
        session = _Session(
            meeting_id=meeting_id,
            vc=vc,
            channel_id=ctx.channel.id,
            started_at=utcnow().isoformat(),
            participants=participants,
        )
        self._sessions[ctx.guild.id] = session

        await asyncio.to_thread(
            self._meetings.create,
            Meeting(
                meeting_id=meeting_id,
                guild_id=str(ctx.guild.id),
                channel_id=str(ctx.channel.id),
                started_at=utcnow(),
                participants=participants,
                gcs_audio_prefix=meeting_id,
                status=MeetingStatus.RECORDING,
            ),
        )

        # per-user で WAV を受信（話者分離が録音時点で確定）
        vc.start_recording(
            discord.sinks.WaveSink(),
            self._on_recording_finished,
            ctx.channel,
            meeting_id,
        )
        await ctx.respond(
            f"🔴 録音を開始しました（{channel.name}）。"
            f"\n※ この会議は録音されます（<#{settings.discord_consent_channel_id}> 参照）。"
        )

    async def stop(self, ctx: discord.ApplicationContext) -> None:
        session = self._sessions.get(ctx.guild.id)
        if not session:
            await ctx.respond("録音は開始されていません。", ephemeral=True)
            return
        session.vc.stop_recording()  # → _on_recording_finished が呼ばれる
        await ctx.respond("⏹️ 録音を停止しました。要約を作成します…")

    async def _on_recording_finished(
        self,
        sink: discord.sinks.WaveSink,
        channel: discord.TextChannel,
        meeting_id: str,
    ) -> None:
        """録音完了コールバック。話者別音声を GCS へ上げて Pub/Sub を発火する。"""
        guild_id = channel.guild.id
        session = self._sessions.pop(guild_id, None)
        speakers = [str(uid) for uid in sink.audio_data]
        log.info("recording_finished", meeting_id=meeting_id, speakers=speakers)

        with contextlib.suppress(Exception):
            await sink.vc.disconnect()

        # 話者別 WAV を GCS へ
        for user_id, audio in sink.audio_data.items():
            data = audio.file.read()
            await asyncio.to_thread(upload_bytes, data, f"{meeting_id}/{user_id}.wav")

        await asyncio.to_thread(
            self._meetings.update_status, meeting_id, MeetingStatus.TRANSCRIBING.value
        )

        # 後段（agent-service）を起動
        await asyncio.to_thread(
            publish,
            settings.pubsub_topic_recording_done,
            {
                "meeting_id": meeting_id,
                "guild_id": str(guild_id),
                "channel_id": str(session.channel_id if session else channel.id),
                "gcs_prefix": meeting_id,
                "speakers": speakers,
            },
        )
        await channel.send(f"録音完了（話者 {len(speakers)} 名）。文字起こしと要約を開始します。")
