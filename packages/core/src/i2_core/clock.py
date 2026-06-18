"""時刻ユーティリティ。タイムゾーンは常に UTC で保持し、表示時に変換する。"""

from __future__ import annotations

from datetime import UTC, datetime


def utcnow() -> datetime:
    return datetime.now(UTC)


def iso_now() -> str:
    return utcnow().isoformat()
