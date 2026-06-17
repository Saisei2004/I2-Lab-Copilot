# I2-Lab-Copilot

研修室専用の AI エージェントサービス。基本操作は **Discord** で完結し、AI・DB はすべて **GCP** で扱えるもののみを使用する。エージェントは **GCP ADK (Agent Development Kit)** + **Vertex AI (Gemini)** で実装する。

## 提供機能

| # | 機能 | 状態 |
|---|------|------|
| ① | Discord & GCP で完結（全 DB / AI は GCP） | 基盤整備中 |
| ② | Discord スラッシュコマンド操作 | 着手予定 |
| ③ | bot による録音 → 文字起こし → 会議要約 | 着手予定 |
| ④ | 会議で出た個人宛フィードバック + AI フィードバックを DM | 着手予定 |
| ⑤ | スケール容易な設計（会議室予約 / 自動情報収集など） | 設計済み |
| ⑦ | 各自の GitHub 報告書（`nakalab/progress2026`）からの情報抽出 | 着手予定 |

## アーキテクチャ

```
Discord ──> discord-bot (Cloud Run, 常時起動) ──GCS/Pub-Sub──> agent-service (Cloud Run)
                                                                  └─ ADK root_agent
                                                                      ├─ meeting_agent
                                                                      ├─ feedback_agent
                                                                      └─ report_agent
GCP データ層: Firestore / Cloud Storage / Secret Manager / Vertex AI / Speech-to-Text
```

詳細は [docs/architecture.md](docs/architecture.md) と [docs/adr/](docs/adr/) を参照。

## モノレポ構成

```
apps/
  discord-bot/     # py-cord: 録音・スラッシュコマンド I/O
  agent-service/   # ADK エージェント実行サービス（HTTP / Pub-Sub 受信）
packages/
  core/            # 設定・ロギング・GCP クライアント共通化 (i2_core)
  storage/         # Firestore / GCS データアクセス (i2_storage)
  integrations/    # GitHub / Discord ヘルパ (i2_integrations)
  agents/          # ADK エージェント定義 (i2_agents)
infra/terraform/   # GCP を IaC 管理
docs/              # 設計・ADR・運用 runbook
```

## 開発環境

前提: `uv` / `python 3.13` / `gcloud` / `docker`（任意で `terraform`）。

```bash
make setup       # 依存解決 + pre-commit
make check       # lint + typecheck + test（CI と同一）
make adk-web     # ADK 開発 UI でエージェントを対話検証
make bot         # Discord bot をローカル起動
```

環境変数は [.env.example](.env.example) を `.env` にコピーして設定（`.env` は gitignore 済み）。本番では Secret Manager から注入する。

## GCP セットアップ

有効化する API・IAM・サービスアカウント・Workload Identity Federation はすべて [infra/terraform/](infra/terraform/) でコード管理。手順は [docs/runbook.md](docs/runbook.md)。

## タスク管理

GitHub Issues + Projects(v2) で運用。Epic → Issue 分解、ラベル、マイルストーンは [.github/](.github/) を参照。

## ⚠️ プライバシー / 録音同意

音声録音は参加者の同意が前提。Discord サーバーの `#録音同意-周知` で周知済み。録音開始時に bot が再通知する運用とする。
