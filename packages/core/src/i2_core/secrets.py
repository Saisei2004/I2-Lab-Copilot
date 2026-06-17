"""Secret Manager アクセス。Cloud Run 上ではサービスアカウント認証で読み取る。"""

from __future__ import annotations

from functools import lru_cache

from google.cloud import secretmanager

from i2_core.config import settings


@lru_cache
def _client() -> secretmanager.SecretManagerServiceClient:
    return secretmanager.SecretManagerServiceClient()


def get_secret(name: str, version: str = "latest") -> str:
    """Secret Manager から最新バージョンの値を取得する。

    Args:
        name: シークレット名（例: "discord-bot-token"）
        version: バージョン（既定 "latest"）
    """
    path = f"projects/{settings.google_cloud_project}/secrets/{name}/versions/{version}"
    response = _client().access_secret_version(name=path)
    return response.payload.data.decode("utf-8")
