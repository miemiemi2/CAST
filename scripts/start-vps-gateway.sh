#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
: "${CAST_PROVIDER:=vertex}"
: "${GOOGLE_CLOUD_PROJECT:=ata-creative-change-2026}"
: "${GOOGLE_CLOUD_LOCATION:=global}"
export CAST_PROVIDER GOOGLE_CLOUD_PROJECT GOOGLE_CLOUD_LOCATION
exec .venv/bin/uvicorn cast.gateway:app --host 127.0.0.1 --port "${CAST_GATEWAY_PORT:-8877}"
