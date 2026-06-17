"""agent-service: FastAPI。

- GET  /healthz            : ヘルスチェック（Cloud Run）
- POST /pubsub/recording   : Pub/Sub push 受信 → 文字起こし→要約→個人FB のパイプライン起動

NOTE: 初期スケルトン。ADK Runner との結線・パイプライン本体は Issue で実装。
"""

from __future__ import annotations

import base64
import json

from fastapi import FastAPI, Request

from i2_core.logging import get_logger

log = get_logger("i2_agent_service")
app = FastAPI(title="i2-agent-service")


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/pubsub/recording")
async def on_recording_done(request: Request) -> dict[str, str]:
    """Pub/Sub push メッセージを受け取り、要約パイプラインを起動する。"""
    envelope = await request.json()
    message = envelope.get("message", {})
    data = {}
    if message.get("data"):
        data = json.loads(base64.b64decode(message["data"]).decode("utf-8"))
    log.info("recording_event", payload=data)

    # TODO(#): パイプライン実装
    #   1. STT: transcription.transcribe_track × 話者数 → merge_tracks
    #   2. meeting_agent で要約 → Discord #要約 へ投稿
    #   3. feedback_agent で個人FB → 各人へ DM
    #   4. Firestore に保存
    return {"status": "accepted"}
