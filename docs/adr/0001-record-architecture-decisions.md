# ADR 0001: アーキテクチャ決定記録を導入する

- Status: Accepted
- Date: 2026-06-18

## Context
意思決定の背景を残し、後から参加するメンバーが「なぜこの構成か」を追えるようにしたい。

## Decision
重要な技術判断は `docs/adr/NNNN-*.md` に ADR として記録する。フォーマットは Context / Decision / Consequences。

## Consequences
- 設計変更時は新しい ADR を追加し、古いものは Status を `Superseded by ADR-NNNN` に更新する。
