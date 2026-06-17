"""Speech-to-Text v2 による文字起こし。

per-user sink で話者ごとに WAV が分かれているため diarization は不要。
各トラックを文字起こしし、開始タイムスタンプでマージして発話ログを作る。

NOTE: 初期スケルトン。recognizer 設定・言語・サンプリングレートは Issue で詰める。
"""

from __future__ import annotations

from i2_core.config import settings
from i2_storage.models import TranscriptSegment


def transcribe_track(
    gcs_uri: str, speaker_id: str, language_code: str = "ja-JP"
) -> list[TranscriptSegment]:
    """1 話者分の WAV(gs://) を文字起こしして TranscriptSegment 列を返す。

    TODO(#): google-cloud-speech v2 (Chirp) の BatchRecognize を実装。
    - recognizer: projects/{project}/locations/{loc}/recognizers/_
    - 長尺は BatchRecognize（GCS 入力）で非同期処理
    """
    _ = (gcs_uri, speaker_id, language_code, settings)  # placeholder
    raise NotImplementedError("STT 実装は Issue で対応（agents/storage と結線）")


def merge_tracks(per_speaker: dict[str, list[TranscriptSegment]]) -> list[TranscriptSegment]:
    """話者別セグメントを start_ms 昇順にマージして 1 本の発話ログにする。"""
    merged: list[TranscriptSegment] = [s for segs in per_speaker.values() for s in segs]
    merged.sort(key=lambda s: s.start_ms)
    return merged
