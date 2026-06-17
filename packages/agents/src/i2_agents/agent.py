"""ADK エージェント構成。

root_agent をオーケストレータとし、3 つの専門 sub-agent に委譲する。
将来のスケール機能（会議室予約・自動情報収集）はツール or sub-agent を追加するだけで拡張可能。

ローカル検証:  `make adk-web`  → ブラウザで対話テスト
"""

from __future__ import annotations

from google.adk.agents import Agent

from i2_agents.prompts import (
    FEEDBACK_INSTRUCTION,
    MEETING_INSTRUCTION,
    REPORT_INSTRUCTION,
    ROOT_INSTRUCTION,
)
from i2_agents.tools import fetch_member_report, list_member_branches
from i2_core.config import settings

# ③ 会議要約
meeting_agent = Agent(
    name="meeting_agent",
    model=settings.gemini_model,
    description="会議の発話ログから要約・決定事項・アクションアイテムを抽出する。",
    instruction=MEETING_INSTRUCTION,
)

# ④ 個人フィードバック
feedback_agent = Agent(
    name="feedback_agent",
    model=settings.gemini_model,
    description="会議内容と報告書から個人向けフィードバックを作成する。",
    instruction=FEEDBACK_INSTRUCTION,
    tools=[fetch_member_report],
)

# ⑦ GitHub 報告書抽出
report_agent = Agent(
    name="report_agent",
    model=settings.gemini_model_fast,
    description="progress2026 のメンバーブランチから報告書を取得・要約する。",
    instruction=REPORT_INSTRUCTION,
    tools=[fetch_member_report, list_member_branches],
)

# root: オーケストレータ
root_agent = Agent(
    name="i2_lab_copilot",
    model=settings.gemini_model,
    description="研修室専用 AI アシスタントのオーケストレータ。",
    instruction=ROOT_INSTRUCTION,
    sub_agents=[meeting_agent, feedback_agent, report_agent],
)
