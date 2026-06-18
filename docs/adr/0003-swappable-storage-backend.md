# ADR 0003: ストレージ backend を差し替え可能にする

- Status: Accepted
- Date: 2026-06-18

## Context
GCP プロジェクト `nakazawa-laborary` で、開発者アカウントに Firestore 作成・IAM 設定の
権限が無く、Firestore を即用意できない。一方で開発は進めたい。本番では Firestore を使う。

## Decision
ストレージを Repository プロトコル（`i2_storage.base`）で抽象化し、`STORAGE_BACKEND` で
実装を選ぶ:
- `memory`: インメモリ（権限不要・既定）。ローカル開発/テスト用。
- `firestore`: Cloud Firestore（本番）。`FIRESTORE_EMULATOR_HOST` 設定時は同一クライアントで
  ローカルエミュレータに接続（コード無改修）。

呼び出し側は `get_meeting_store()` / `get_feedback_store()` のみ使用し、具象に依存しない。

## Consequences
- 権限が揃う前でも `memory` で開発・テストが回る。
- 管理者が Firestore を作成したら `STORAGE_BACKEND=firestore` に変えるだけで本番化（コード変更なし）。
- memory は永続しないため本番不可。CI/本番では firestore を必須とする（起動時バリデーションは別 Issue）。
- 新コレクション追加時は protocol と両実装を更新する必要がある。
