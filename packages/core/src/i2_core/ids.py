"""ID 生成。会議 ID は guild とランダム接尾辞で衝突を避ける。"""

from __future__ import annotations

import uuid


def new_meeting_id(guild_id: int) -> str:
    return f"{guild_id}-{uuid.uuid4().hex[:12]}"


def new_feedback_id() -> str:
    return uuid.uuid4().hex
