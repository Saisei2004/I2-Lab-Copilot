# バックログ（Epic → Issue）

`gh auth login` 後に `gh issue create` で起票する初期バックログ。ラベルは `.github/labels.yml` 参照。

## Epic A: ② Discord コマンド基盤
- [ ] `/ping` 動作確認（done: 実装済み）
- [ ] `/record start|stop` の堅牢化（多重録音防止・例外時クリーンアップ）
- [ ] `/report <member>` 報告書要約コマンド（report_agent 呼び出し）
- [ ] `/summary <meeting_id>` 過去会議の再要約
- [ ] エラー通知の ephemeral 統一・権限チェック

## Epic B: ③ 録音 → 文字起こし → 要約
- [ ] 録音 → GCS/Firestore/PubSub 結線（done: 実装済み・要 GCP 実機検証）
- [ ] STT v2 のリージョン/モデル確定（asia-northeast1 で動くモデル検証）
- [ ] 長尺会議の STT 出力を GCS 出力方式へ（inline 制限回避）
- [ ] 要約フォーマット確定（トピック/決定/アクション）と Firestore 保存
- [ ] パイプラインの冪等化（再配信耐性）

## Epic C: ④ 個人フィードバック
- [ ] feedback_agent: 会議中の他者指摘抽出（source=meeting）の精度向上
- [ ] DM 配信と delivered_at 記録
- [ ] 本人の GitHub 報告書を文脈に取り込み（report_agent 連携）
- [ ] オプトアウト（FB を受け取らない設定）

## Epic D: ⑦ GitHub 報告書抽出
- [ ] progress2026 ブランチ ↔ メンバー（discord_user_id）対応付け（users コレクション）
- [ ] 不定形ディレクトリからのテキスト収集（done: tools 実装済み）
- [ ] 報告書の定期インデックス（Firestore vector search）

## Epic E: 基盤 / Infra
- [ ] Terraform apply（API/IAM/Firestore/GCS/PubSub/WIF）
- [ ] CI から WIF で Cloud Run デプロイ（GitHub Actions）
- [ ] Pub/Sub push サブスクの URL 設定（agent-service デプロイ後）
- [ ] Secret 投入（discord-bot-token / github-readonly-token）
- [ ] 監視・アラート（Cloud Monitoring）

## Epic F: ⑤ 将来スケール（未着手）
- [ ] 会議室予約ツール（Firestore + Calendar API）
- [ ] 自動情報収集ツール（Grounding / google_search）
- [ ] RAG 横断検索（会議録 + 報告書）
