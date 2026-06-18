"""アプリ全体の設定。環境変数 / .env から読み込む（pydantic-settings）。

本番(Cloud Run)では環境変数として Secret Manager の値を注入する。
ローカルはリポジトリ直下の .env を使う。
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # GCP
    google_cloud_project: str = Field(default="nakazawa-laborary")
    google_cloud_location: str = Field(default="asia-northeast1")
    google_genai_use_vertexai: bool = Field(default=True)

    # Storage
    gcs_bucket_recordings: str = Field(default="i2-lab-copilot-recordings")
    # データ backend: "memory"（権限不要・既定） | "firestore"（本番）
    # firestore + FIRESTORE_EMULATOR_HOST 設定でローカルエミュレータに接続できる
    storage_backend: str = Field(default="memory")

    # Models
    gemini_model: str = Field(default="gemini-2.5-pro")
    gemini_model_fast: str = Field(default="gemini-2.5-flash")

    # Discord
    discord_bot_token: str = Field(default="")
    discord_guild_id: int = Field(default=0)
    discord_consent_channel_id: int = Field(default=0)
    discord_summary_channel_id: int = Field(default=0)

    # GitHub（報告書ソース）
    github_reports_owner: str = Field(default="nakalab")
    github_reports_repo: str = Field(default="progress2026")
    github_token: str = Field(default="")

    # Pub/Sub
    pubsub_topic_recording_done: str = Field(default="recording-done")

    # Logging
    log_level: str = Field(default="INFO")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
