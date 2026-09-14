#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
: "${CAST_AGENT_URL:=http://127.0.0.1:18765}"
export CAST_AGENT_URL
exec .venv-cast/bin/uvicorn cast.app:app --host 127.0.0.1 --port "${CAST_PORT:-8765}"
