# ADR 0002: 技術スタック選定

- Status: Accepted
- Date: 2026-06-18

## Context
研修室内専用の AI エージェントを Discord 操作・GCP 完結で構築する。録音（voice receive）・会議要約・個人 FB・GitHub 報告書抽出が初期スコープ。

## Decision

| 領域 | 採用 | 理由 |
|------|------|------|
| エージェント基盤 | GCP ADK (Python) | 要件指定。ツール追加でスケール容易 |
| LLM | Vertex AI Gemini 2.5 | GCP 完結・ADK 標準 |
| Discord bot | py-cord | voice receive 対応、ADK と Python 統一 |
| 文字起こし | Speech-to-Text v2 (Chirp) | GCP 完結、per-user sink と相性良 |
| DB | Firestore | サーバーレス、ネイティブ vector 検索、スケール容易 |
| 音声保存 | Cloud Storage | 標準 |
| 実行基盤 | Cloud Run (min-instances=1) | Gateway 常時接続を維持しつつサーバーレス |
| シークレット | Secret Manager | 鍵をコードに置かない |
| IaC | Terraform | GCP リソースのコード管理 |
| モノレポ | uv workspace | 高速・モダン、Python 単一言語に最適 |
| CI/CD | GitHub Actions + WIF | 鍵レスで GCP 連携 |

## Consequences
- 単一言語（Python）でモノレポがシンプル。Node 依存を持たない。
- Cloud Run 常時起動のため最小コストが発生（min-instances=1）。研修室規模では許容。
- discord.js の voice 実績を捨てるが、py-cord で要件を満たせる前提。問題が出れば録音部のみ別サービス化を検討（ADR 追記）。
