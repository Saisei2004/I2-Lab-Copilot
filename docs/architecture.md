# アーキテクチャ

## 1. 目的と原則

- **Discord 完結**: 利用者の操作・出力はすべて Discord（スラッシュコマンド / DM / チャンネル投稿）。
- **GCP 完結**: AI・DB・ストレージ・実行基盤はすべて GCP のマネージドサービスのみ。
- **スケール容易**: 新機能は ADK エージェントに「ツール」を足す形で拡張する（会議室予約・自動情報収集など）。
- **最小権限 / 鍵レス**: シークレットは Secret Manager、CI は Workload Identity Federation（鍵ファイルを置かない）。

## 2. コンポーネント

### discord-bot（Cloud Run / 常時起動）
- py-cord で Discord Gateway に常時接続（`min-instances=1`, CPU always allocated）。
- スラッシュコマンド受付（②）、ボイス録音（③, py-cord の per-user `WaveSink`）。
- 録音停止時に話者ごとの WAV を GCS へ保存し、Pub/Sub `recording-done` を publish。
- 軽い応答は同期、重い処理（要約等）は非同期に逃がす。

### agent-service（Cloud Run）
- Pub/Sub push と HTTP を受け、ADK の `root_agent` を実行。
- ADK ローカル検証は `adk web`、本番は Cloud Run（将来 Vertex AI Agent Engine も選択可）。

### ADK エージェント（packages/agents）
- `root_agent`: 意図を判定し sub-agent / tool に委譲するオーケストレータ。
- `meeting_agent`: 文字起こし結果 → 要約・決定事項・アクションアイテム。
- `feedback_agent`: 発言から個人宛の指摘を抽出 + AI フィードバック生成 → 本人へ DM。
- `report_agent`: `nakalab/progress2026` の各ブランチ（不定形）から各自の報告書を抽出し文脈に利用。

## 3. データフロー（録音 → 要約 → 個人 FB）

```
/record start ─> bot が VC 参加, WaveSink 録音開始
/record stop  ─> 話者別 WAV を GCS へ ─> Pub/Sub: recording-done
                                            │
agent-service が受信 ─> Speech-to-Text v2 (Chirp) で各トラック文字起こし
                     ─> タイムスタンプでマージし発話ログ生成
                     ─> meeting_agent: 要約 ─> #要約チャンネルへ投稿
                     ─> feedback_agent: 個人別 FB ─> 各人へ DM
                     ─> Firestore に会議・FB・トランスクリプトを保存
```

話者分離は per-user sink により録音時点で確定するため、STT 側の diarization に依存せず精度が安定する。

## 4. GCP サービス対応表

| 役割 | サービス |
|------|---------|
| LLM / エージェント | Vertex AI (Gemini 2.5) + ADK |
| 文字起こし | Speech-to-Text v2 (Chirp) |
| 構造化 DB / ベクトル検索 | Firestore (native vector search) |
| 音声 / 成果物保存 | Cloud Storage |
| シークレット | Secret Manager |
| 非同期連携 | Pub/Sub |
| 定期実行 / 再試行 | Cloud Scheduler / Cloud Tasks |
| 実行基盤 | Cloud Run |
| 監視 | Cloud Logging / Monitoring |

## 5. Firestore データモデル（暫定）

```
users/{discord_user_id}
  display_name, github_username, report_branch, created_at
meetings/{meeting_id}
  guild_id, channel_id, started_at, ended_at, participants[], gcs_audio_prefix,
  status: recording|transcribing|summarizing|done|error
meetings/{meeting_id}/transcript/{segment_id}
  speaker_id, start_ms, end_ms, text
meetings/{meeting_id}/summary
  topics[], decisions[], action_items[{assignee, text, due}], raw
feedback/{feedback_id}
  meeting_id, target_user_id, source: meeting|ai, text, created_at, delivered_at
```

## 6. スケール拡張（⑤・未実装）

ADK のツール追加で対応する想定:
- `room_reservation_tool`: 会議室予約（Firestore + Google Calendar API）。
- `web_research_tool`: 自動情報収集（ADK 組み込み Google Search / Vertex AI Grounding）。
- RAG: 会議録・報告書を Firestore vector search でインデックスし横断検索。

## 7. セキュリティ / プライバシー

- 録音は同意前提（`#録音同意-周知`）。録音開始時に bot が再通知。
- 個人フィードバックは DM のみ（公開チャンネルに出さない）。
- シークレットはコード/リポジトリに置かず Secret Manager 管理。
- サービスアカウントは機能ごと最小権限。
