"""ADK ツール（関数ツール）。エージェントはこれらを呼び出して機能を実現する。

スケール拡張（⑤）はここにツールを追加する形で行う:
  - room_reservation: 会議室予約（Firestore + Calendar）
  - web_research: 自動情報収集（ADK 組み込み google_search / Grounding）
"""

from __future__ import annotations

from i2_integrations import github_reports


def fetch_member_report(branch: str, max_files: int = 20) -> dict:
    """指定メンバー（progress2026 のブランチ）の報告書テキストを収集して返す。

    報告書は不定形のため、テキスト/Markdown を集めて LLM 側で解釈させる。

    Args:
        branch: progress2026 上のブランチ名（メンバー単位）
        max_files: 取得する最大ファイル数
    Returns:
        {"branch", "files": [{"path", "text"}]}
    """
    text_exts = (".md", ".txt", ".rst", ".org")
    paths = [p for p in github_reports.list_files(branch) if p.lower().endswith(text_exts)]
    files = []
    for path in paths[:max_files]:
        try:
            files.append({"path": path, "text": github_reports.read_text_file(branch, path)})
        except Exception as exc:
            files.append({"path": path, "text": f"<読み取り失敗: {exc}>"})
    return {"branch": branch, "files": files}


def list_member_branches() -> list[str]:
    """報告書リポジトリのブランチ（=メンバー）一覧を返す。"""
    return github_reports.list_branches()
