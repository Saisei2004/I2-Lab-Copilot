"""Cloud Storage アクセス。録音 WAV のアップロード / 署名 URL 等。"""

from __future__ import annotations

from functools import lru_cache

from google.cloud import storage

from i2_core.config import settings


@lru_cache
def _client() -> storage.Client:
    return storage.Client(project=settings.google_cloud_project)


def upload_file(local_path: str, blob_name: str) -> str:
    """ローカルファイルを録音バケットへアップロードし gs:// URI を返す。"""
    bucket = _client().bucket(settings.gcs_bucket_recordings)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(local_path)
    return f"gs://{settings.gcs_bucket_recordings}/{blob_name}"


def upload_bytes(data: bytes, blob_name: str, content_type: str = "audio/wav") -> str:
    bucket = _client().bucket(settings.gcs_bucket_recordings)
    blob = bucket.blob(blob_name)
    blob.upload_from_string(data, content_type=content_type)
    return f"gs://{settings.gcs_bucket_recordings}/{blob_name}"
