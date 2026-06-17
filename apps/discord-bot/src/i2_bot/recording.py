"""録音（③）。py-cord の voice receive (WaveSink) で話者ごとに録音する。

フロー:
  start → VC 接続 → WaveSink で録音開始 → 同意メッセージ再通知
  stop  → 録音停止 → 話者別 WAV を GCS へ → Pub/Sub(recording-done) を publish
          → 以降は agent-service が文字起こし→要約→個人FBを担当

NOTE: 初期スケルトン。会議メタの Firestore 登録・Pub/Sub publish は Issue で結線。
"""

from __future__ import annotations

import discord

from i2_core.config import settings
from i2_core.logging import get_logger

log = get_logger("i2_bot.recording")


class RecordingManager:
    """guild ごとの録音状態を管理する。"""

    def __init__(self) -> None:
        self._connections: dict[int, discord.VoiceClient] = {}

    async def start(self, ctx: discord.ApplicationContext) -> None:
        channel = ctx.author.voice.channel
        vc = await channel.connect()
        self._connections[ctx.guild.id] = vc

        # per-user で WAV を受信（話者分離が録音時点で確定）
        vc.start_recording(
            discord.sinks.WaveSink(),
            self._on_recording_finished,
            ctx.channel,
        )
        await ctx.respond(
            f"🔴 録音を開始しました（{channel.name}）。"
            f"\n※ この会議は録音されます（<#{settings.discord_consent_channel_id}> 参照）。",
        )

    async def stop(self, ctx: discord.ApplicationContext) -> None:
        vc = self._connections.get(ctx.guild.id)
        if not vc:
            await ctx.respond("録音は開始されていません。", ephemeral=True)
            return
        vc.stop_recording()  # → _on_recording_finished が呼ばれる
        await ctx.respond("⏹️ 録音を停止しました。要約を作成します…")

    async def _on_recording_finished(
        self, sink: discord.sinks.WaveSink, channel: discord.TextChannel, *args
    ) -> None:
        """録音完了コールバック。話者別音声を GCS へ上げて Pub/Sub を発火する。"""
        # sink.audio_data: {user_id: AudioData(file=BytesIO)}
        speakers = list(sink.audio_data.keys())
        log.info("recording_finished", speakers=speakers)

        # TODO(#): GCS アップロード + Firestore 会議登録 + Pub/Sub publish
        #   for uid, audio in sink.audio_data.items():
        #       upload_bytes(audio.file.read(), f"{meeting_id}/{uid}.wav")
        #   publish(settings.pubsub_topic_recording_done, {"meeting_id": ...})
        await channel.send(f"録音完了（話者 {len(speakers)} 名）。文字起こしを開始します。")
