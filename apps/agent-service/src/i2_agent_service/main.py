"""agent-service: FastAPI。

- GET  /healthz            : ヘルスチェック（Cloud Run）
- POST /pubsub/recording   : Pub/Sub push 受信 → 文字起こし→要約→個人FB のパイプライン起動

長尺会議では STT が ack 期限を超え得るため、サブスクリプションの ack_deadline は長めに設定し、
失敗時は Pub/Sub の再配信に任せる（パイプラインは冪等性を意識して実装する）。
"""

from __future__ import annotations

import base64
import json

from fastapi import FastAPI, Request

from i2_agent_service.pipeline import RecordingEvent, run_pipeline
from i2_core.logging import get_logger

log = get_logger("i2_agent_service")
app = FastAPI(title="i2-agent-service")


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


def _decode_pubsub(envelope: dict) -> dict:
    message = envelope.get("message", {})
    if message.get("data"):
        return json.loads(base64.b64decode(message["data"]).decode("utf-8"))
    return {}


@app.post("/pubsub/recording")
async def on_recording_done(request: Request) -> dict[str, str]:
    """Pub/Sub push メッセージを受け取り、要約パイプラインを実行する。"""
    payload = _decode_pubsub(await request.json())
    log.info("recording_event", payload=payload)
    if not payload:
        return {"status": "ignored"}

    event = RecordingEvent(**payload)
    await run_pipeline(event)
    return {"status": "done", "meeting_id": event.meeting_id}
