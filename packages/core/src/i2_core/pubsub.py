"""Pub/Sub 発行ヘルパ。録音完了などのイベントを非同期に流す。"""

from __future__ import annotations

import json
from functools import lru_cache

from google.cloud import pubsub_v1

from i2_core.config import settings


@lru_cache
def _publisher() -> pubsub_v1.PublisherClient:
    return pubsub_v1.PublisherClient()


def publish(topic: str, payload: dict) -> str:
    """payload を JSON にして topic へ publish し、message_id を返す。"""
    client = _publisher()
    topic_path = client.topic_path(settings.google_cloud_project, topic)
    future = client.publish(topic_path, json.dumps(payload).encode("utf-8"))
    return future.result()
