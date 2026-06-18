"""ADK エージェントをプログラムから 1 ショット実行するヘルパ。

agent-service のパイプラインから meeting_agent / feedback_agent を呼ぶために使う。
google-adk の InMemoryRunner を用いる（会話状態を保持しない単発実行）。
"""

from __future__ import annotations

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

_APP_NAME = "i2_lab_copilot"


async def run_agent_text(agent: Agent, prompt: str, *, user_id: str = "system") -> str:
    """agent に prompt を渡し、最終応答テキストを返す。"""
    runner = InMemoryRunner(agent=agent, app_name=_APP_NAME)
    session = await runner.session_service.create_session(app_name=_APP_NAME, user_id=user_id)
    message = types.Content(role="user", parts=[types.Part(text=prompt)])

    final = ""
    async for event in runner.run_async(
        user_id=user_id, session_id=session.id, new_message=message
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final = event.content.parts[0].text or final
    return final
