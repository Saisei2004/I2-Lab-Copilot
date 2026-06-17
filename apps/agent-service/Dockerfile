# syntax=docker/dockerfile:1
FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY . /app

RUN uv sync --package i2-agent-service --no-dev --frozen

ENV PYTHONUNBUFFERED=1 PORT=8080
CMD ["uv", "run", "--no-sync", "--package", "i2-agent-service", \
     "uvicorn", "i2_agent_service.main:app", "--host", "0.0.0.0", "--port", "8080"]
