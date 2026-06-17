# syntax=docker/dockerfile:1
FROM python:3.13-slim

# py-cord[voice] の依存（音声処理に libopus/ffmpeg）
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg libopus0 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY . /app

# ワークスペースから discord-bot のみ解決してインストール
RUN uv sync --package i2-discord-bot --no-dev --frozen

ENV PYTHONUNBUFFERED=1
CMD ["uv", "run", "--no-sync", "--package", "i2-discord-bot", "python", "-m", "i2_bot.main"]
