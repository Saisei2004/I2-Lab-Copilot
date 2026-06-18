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
        # ボイス接続は3秒を超え得るため、先に defer して interaction を延長する
        await ctx.defer()

        if ctx.guild.id in self._sessions:
            await ctx.followup.send(
                "既に録音中です。`/record stop` で停止してください。", ephemeral=True
            )
            return

        channel = ctx.author.voice.channel
        try:
            vc = await channel.connect()
        except Exception as exc:
            log.warning("voice_connect_failed", error=str(exc))
            await ctx.followup.send(f"ボイス接続に失敗しました: {exc}", ephemeral=True)
            return
        meeting_id = new_meeting_id(ctx.guild.id)
        participants = [str(m.id) for m in channel.members if not m.bot]

        # per-user で WAV を受信（話者分離が録音時点で確定）。
        # 注意: Discord の DAVE(E2EE) 展開により py-cord の voice receive は現在
        # 動作しないことがある（pycord #3139）。失敗しても固まらないよう捕捉する。
        try:
            vc.start_recording(
                discord.sinks.WaveSink(),
                self._on_recording_finished,
                ctx.channel,
                meeting_id,
            )
        except Exception as exc:
            log.warning("start_recording_failed", error=str(exc))
            with contextlib.suppress(Exception):
                await vc.disconnect()
            await ctx.followup.send(
                "⚠️ 録音を開始できませんでした。\n"
                "Discord の音声E2E暗号化(DAVE)の影響で、py-cord の録音(voice receive)機能が"
                "現在動作しません（上流の既知issue #3139）。\n"
                "コマンドや要約パイプライン等、他機能は利用可能です。",
                ephemeral=True,
            )
            return

        # 録音開始に成功したらセッション登録
        self._sessions[ctx.guild.id] = _Session(
            meeting_id=meeting_id,
            vc=vc,
            channel_id=ctx.channel.id,
            started_at=utcnow().isoformat(),
            participants=participants,
        )
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
        msg = f"🔴 録音を開始しました（{channel.name}）。"
        if settings.discord_consent_channel_id:
            msg += f"\n※ この会議は録音されます（<#{settings.discord_consent_channel_id}> 参照）。"
        await ctx.followup.send(msg)

    async def stop(self, ctx: discord.ApplicationContext) -> None:
        await ctx.defer()
        session = self._sessions.pop(ctx.guild.id, None)
        if not session:
            await ctx.followup.send("録音は開始されていません。", ephemeral=True)
            return
        try:
            session.vc.stop_recording()  # → _on_recording_finished が呼ばれる
        except Exception as exc:
            log.warning("stop_recording_failed", error=str(exc))
            with contextlib.suppress(Exception):
                await session.vc.disconnect()
            await ctx.followup.send(f"停止処理でエラーが発生しました: {exc}", ephemeral=True)
            return
        await ctx.followup.send("⏹️ 録音を停止しました。後処理（保存・要約）を実行します…")

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

        # 取り残し防止: まず必ず VC から退出する
        with contextlib.suppress(Exception):
            await sink.vc.disconnect()

        if not speakers:
            await channel.send("録音を停止しました（音声データなし）。")
            return

        # GCS 保存 → Pub/Sub 発火。権限が無い環境ではここで失敗するが、
        # Bot は落とさずユーザーに状況を伝える。
        try:
            for user_id, audio in sink.audio_data.items():
                data = audio.file.read()
                await asyncio.to_thread(upload_bytes, data, f"{meeting_id}/{user_id}.wav")
            await asyncio.to_thread(
                self._meetings.update_status, meeting_id, MeetingStatus.TRANSCRIBING.value
            )
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
        except Exception as exc:
            log.warning("post_recording_failed", meeting_id=meeting_id, error=str(exc))
            await channel.send(
                f"録音は完了（話者 {len(speakers)} 名）。"
                f"ただし保存/要約はGCP権限が未設定のためスキップしました。"
            )
            return

        await channel.send(f"録音完了（話者 {len(speakers)} 名）。文字起こしと要約を開始します。")
