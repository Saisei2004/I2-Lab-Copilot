"""Discord bot 起動。Cloud Run 上で min-instances=1 / CPU always allocated で常駐させる。

トークンは本番では Secret Manager(discord-bot-token)、ローカルでは .env から取得。
"""

from __future__ import annotations

import discord

from i2_bot.commands import setup_commands
from i2_core.config import settings
from i2_core.logging import get_logger

log = get_logger("i2_bot")


def build_bot() -> discord.Bot:
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    intents.voice_states = True
    # guild 限定にするとスラッシュコマンドが即時反映される
    bot = discord.Bot(intents=intents, debug_guilds=[settings.discord_guild_id])
    setup_commands(bot)

    @bot.event
    async def on_ready() -> None:
        log.info("bot_ready", user=str(bot.user), guild=settings.discord_guild_id)

    return bot


def _resolve_token() -> str:
    if settings.discord_bot_token:
        return settings.discord_bot_token
    # 本番: Secret Manager から取得
    from i2_core.secrets import get_secret

    return get_secret("discord-bot-token")


def main() -> None:
    bot = build_bot()
    bot.run(_resolve_token())


if __name__ == "__main__":
    main()
