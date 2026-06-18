"""Discord REST クライアント（送信専用）。

agent-service は Gateway を持たないため、要約投稿・個人 DM は REST API で行う。
Bot Token は .env か Secret Manager(discord-bot-token) から解決する。
"""

from __future__ import annotations

import httpx

from i2_core.config import settings

_API = "https://discord.com/api/v10"
_MAX_LEN = 2000  # Discord メッセージ本文の上限


def _token() -> str:
    if settings.discord_bot_token:
        return settings.discord_bot_token
    from i2_core.secrets import get_secret

    return get_secret("discord-bot-token")


def _headers() -> dict[str, str]:
    return {"Authorization": f"Bot {_token()}", "Content-Type": "application/json"}


def _chunks(content: str) -> list[str]:
    """2000 字制限に合わせて改行優先で分割する。"""
    if len(content) <= _MAX_LEN:
        return [content]
    parts: list[str] = []
    buf = ""
    for line in content.splitlines(keepends=True):
        if len(buf) + len(line) > _MAX_LEN:
            if buf:
                parts.append(buf)
            buf = line
        else:
            buf += line
    if buf:
        parts.append(buf)
    return parts


def post_message(channel_id: int, content: str) -> None:
    """チャンネルへ投稿（長文は分割送信）。"""
    with httpx.Client(timeout=30) as client:
        for part in _chunks(content):
            r = client.post(
                f"{_API}/channels/{channel_id}/messages",
                headers=_headers(),
                json={"content": part},
            )
            r.raise_for_status()


def send_dm(user_id: int, content: str) -> None:
    """ユーザーへ DM（DM チャンネルを開いてから投稿）。"""
    with httpx.Client(timeout=30) as client:
        r = client.post(
            f"{_API}/users/@me/channels",
            headers=_headers(),
            json={"recipient_id": str(user_id)},
        )
        r.raise_for_status()
        dm_channel_id = r.json()["id"]
        for part in _chunks(content):
            r2 = client.post(
                f"{_API}/channels/{dm_channel_id}/messages",
                headers=_headers(),
                json={"content": part},
            )
            r2.raise_for_status()
