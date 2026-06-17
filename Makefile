.DEFAULT_GOAL := help
SHELL := /bin/bash

.PHONY: help setup sync fmt lint typecheck test check bot agent adk-web tf-init tf-plan

help: ## このヘルプを表示
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

setup: ## 初回セットアップ（依存解決 + pre-commit）
	uv sync --all-packages --dev
	uv run pre-commit install

sync: ## 依存を解決
	uv sync --all-packages --dev

fmt: ## フォーマット
	uv run ruff format .
	uv run ruff check --fix .

lint: ## Lint
	uv run ruff check .

typecheck: ## 型チェック
	uv run pyright

test: ## テスト
	uv run pytest

check: lint typecheck test ## CIと同じ一括チェック

bot: ## Discord bot をローカル起動
	uv run --package i2-discord-bot python -m i2_bot.main

agent: ## agent-service をローカル起動
	uv run --package i2-agent-service python -m i2_agent_service.main

adk-web: ## ADK 開発UIを起動（エージェント検証）
	uv run adk web packages/agents/src/i2_agents

tf-init: ## Terraform 初期化
	cd infra/terraform && terraform init

tf-plan: ## Terraform 差分確認
	cd infra/terraform && terraform plan
