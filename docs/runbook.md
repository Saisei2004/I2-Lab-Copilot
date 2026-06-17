# 運用 Runbook（初期セットアップ）

GCP プロジェクト: `nakazawa-laborary` / 推奨リージョン: `asia-northeast1`

## 0. 前提
- `gcloud` がインストール済み・対象プロジェクトで認証済み
- 課金が有効
- オーナー or 編集者相当の権限

## 1. gcloud 初期設定
```bash
gcloud auth login
gcloud config set project nakazawa-laborary
gcloud auth application-default login   # ローカル ADC
```

## 2. API 有効化（Terraform でも実施されるが手動なら）
```bash
gcloud services enable \
  aiplatform.googleapis.com speech.googleapis.com firestore.googleapis.com \
  storage.googleapis.com secretmanager.googleapis.com run.googleapis.com \
  cloudbuild.googleapis.com artifactregistry.googleapis.com pubsub.googleapis.com \
  cloudtasks.googleapis.com cloudscheduler.googleapis.com \
  logging.googleapis.com monitoring.googleapis.com \
  iam.googleapis.com iamcredentials.googleapis.com cloudresourcemanager.googleapis.com
```

## 3. シークレット登録（Secret Manager）
```bash
# Discord Bot Token（Developer Portal で発行した値）
printf '%s' 'YOUR_DISCORD_BOT_TOKEN' | \
  gcloud secrets create discord-bot-token --data-file=- --replication-policy=automatic

# GitHub 参照用トークン（progress2026 read 権限）
printf '%s' 'YOUR_GITHUB_TOKEN' | \
  gcloud secrets create github-readonly-token --data-file=- --replication-policy=automatic
```
> 既に存在する場合は `gcloud secrets versions add <name> --data-file=-` で更新。

## 4. インフラ構築（Terraform）
```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars   # 値を編集
terraform init
terraform plan
terraform apply
```
作成物: API 有効化 / サービスアカウント / IAM / Firestore / GCS バケット / Pub/Sub / Artifact Registry / WIF（GitHub Actions 用）。

## 5. デプロイ（暫定・手動）
```bash
# Artifact Registry へ push → Cloud Run デプロイ（CI 整備までの暫定）
gcloud run deploy i2-discord-bot --source apps/discord-bot \
  --region asia-northeast1 --min-instances 1 --no-cpu-throttling \
  --service-account i2-copilot-sa@nakazawa-laborary.iam.gserviceaccount.com
```

## 6. 動作確認
- Discord で `/ping` が応答するか
- `/record start` → `/record stop` で GCS に音声が出力されるか
- Pub/Sub → agent-service → 要約投稿まで通るか

## トラブルシュート
- bot がオフライン: Cloud Run の min-instances と CPU always allocated を確認。
- 文字起こし空: STT のリージョン・サンプリングレート・WAV ヘッダを確認。
- 権限エラー: サービスアカウントのロール（Terraform `iam.tf`）を確認。
