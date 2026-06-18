"""Speech-to-Text v2 による文字起こし。

per-user sink で話者ごとに WAV が分かれているため diarization は不要。
各トラックを文字起こしし、開始タイムスタンプでマージして発話ログを作る。

注意:
- Chirp 系モデルはリージョン依存。asia-northeast1 で未提供の場合は
  GOOGLE_CLOUD_LOCATION を us-central1 等にするか model を "long" に変更する。
- location != "global" のときは regional エンドポイントを指定する必要がある。
- 実呼び出しは GCP 認証が要るためローカル単体テストではモックする。
"""

from __future__ import annotations

from datetime import timedelta
from functools import lru_cache

from google.api_core.client_options import ClientOptions
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech

from i2_core.config import settings
from i2_storage.models import TranscriptSegment

# モデルはリージョンに合わせて調整（既定は汎用の long）
_STT_MODEL = "long"


@lru_cache
def _client() -> SpeechClient:
    location = settings.google_cloud_location
    if location == "global":
        return SpeechClient()
    endpoint = f"{location}-speech.googleapis.com"
    return SpeechClient(client_options=ClientOptions(api_endpoint=endpoint))


def _ms(offset: timedelta | None) -> int:
    return int(offset.total_seconds() * 1000) if offset else 0


def transcribe_track(
    gcs_uri: str, speaker_id: str, language_code: str = "ja-JP"
) -> list[TranscriptSegment]:
    """1 話者分の WAV(gs://) を文字起こしして TranscriptSegment 列を返す。"""
    project = settings.google_cloud_project
    location = settings.google_cloud_location
    recognizer = f"projects/{project}/locations/{location}/recognizers/_"

    config = cloud_speech.RecognitionConfig(
        auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
        language_codes=[language_code],
        model=_STT_MODEL,
        features=cloud_speech.RecognitionFeatures(enable_word_time_offsets=True),
    )
    request = cloud_speech.BatchRecognizeRequest(
        recognizer=recognizer,
        config=config,
        files=[cloud_speech.BatchRecognizeFileMetadata(uri=gcs_uri)],
        recognition_output_config=cloud_speech.RecognitionOutputConfig(
            inline_response_config=cloud_speech.InlineOutputConfig(),
        ),
    )
    operation = _client().batch_recognize(request=request)
    response = operation.result(timeout=900)

    segments: list[TranscriptSegment] = []
    file_result = response.results.get(gcs_uri)
    if not file_result or not file_result.transcript:
        return segments
    for result in file_result.transcript.results:
        if not result.alternatives:
            continue
        alt = result.alternatives[0]
        words = list(alt.words)
        start = _ms(words[0].start_offset) if words else 0
        end = _ms(words[-1].end_offset) if words else 0
        segments.append(
            TranscriptSegment(
                speaker_id=speaker_id, start_ms=start, end_ms=end, text=alt.transcript
            )
        )
    return segments


def merge_tracks(per_speaker: dict[str, list[TranscriptSegment]]) -> list[TranscriptSegment]:
    """話者別セグメントを start_ms 昇順にマージして 1 本の発話ログにする。"""
    merged: list[TranscriptSegment] = [s for segs in per_speaker.values() for s in segs]
    merged.sort(key=lambda s: s.start_ms)
    return merged


def transcript_to_text(segments: list[TranscriptSegment]) -> str:
    """LLM 入力用に「[話者] 本文」形式のプレーンテキストへ整形する。"""
    return "\n".join(f"[{s.speaker_id}] {s.text}" for s in segments)
