"""GitHub 報告書（nakalab/progress2026）からの情報抽出。

progress2026 は各自がブランチごとに不定形のディレクトリ構成で進捗を置いている。
ブランチ一覧 → ツリー走査 → Markdown/テキストを収集する低レベル API を提供し、
構造化（要約・抽出）は agents 側の report_agent が LLM で行う。
"""

from __future__ import annotations

import httpx

from i2_core.config import settings

_API = "https://api.github.com"


def _headers() -> dict[str, str]:
    h = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if settings.github_token:
        h["Authorization"] = f"Bearer {settings.github_token}"
    return h


def list_branches() -> list[str]:
    """progress2026 のブランチ一覧（= 各メンバーの作業単位）を返す。"""
    owner, repo = settings.github_reports_owner, settings.github_reports_repo
    branches: list[str] = []
    page = 1
    with httpx.Client(timeout=30) as client:
        while True:
            r = client.get(
                f"{_API}/repos/{owner}/{repo}/branches",
                headers=_headers(),
                params={"per_page": 100, "page": page},
            )
            r.raise_for_status()
            chunk = r.json()
            if not chunk:
                break
            branches.extend(b["name"] for b in chunk)
            page += 1
    return branches


def list_files(branch: str) -> list[str]:
    """指定ブランチのファイルパス一覧（再帰ツリー）。"""
    owner, repo = settings.github_reports_owner, settings.github_reports_repo
    with httpx.Client(timeout=30) as client:
        r = client.get(
            f"{_API}/repos/{owner}/{repo}/git/trees/{branch}",
            headers=_headers(),
            params={"recursive": "1"},
        )
        r.raise_for_status()
        tree = r.json().get("tree", [])
    return [n["path"] for n in tree if n.get("type") == "blob"]


def read_text_file(branch: str, path: str) -> str:
    """テキストファイル本文を取得（raw）。"""
    owner, repo = settings.github_reports_owner, settings.github_reports_repo
    url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"
    with httpx.Client(timeout=30, follow_redirects=True) as client:
        r = client.get(url, headers=_headers())
        r.raise_for_status()
        return r.text
