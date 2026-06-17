"""スラッシュコマンド定義（②）。録音操作は recording.py に委譲する。"""

from __future__ import annotations

import discord

from i2_bot.recording import RecordingManager
from i2_core.logging import get_logger

log = get_logger("i2_bot.commands")
_recordings = RecordingManager()


def setup_commands(bot: discord.Bot) -> None:
    @bot.slash_command(description="疎通確認")
    async def ping(ctx: discord.ApplicationContext) -> None:
        await ctx.respond("pong 🏓")

    record = bot.create_group("record", "会議の録音操作")

    @record.command(name="start", description="現在のVCで録音を開始")
    async def record_start(ctx: discord.ApplicationContext) -> None:
        if not (ctx.author.voice and ctx.author.voice.channel):
            await ctx.respond("先にボイスチャンネルに参加してください。", ephemeral=True)
            return
        await _recordings.start(ctx)

    @record.command(name="stop", description="録音を停止し、要約処理を起動")
    async def record_stop(ctx: discord.ApplicationContext) -> None:
        await _recordings.stop(ctx)
