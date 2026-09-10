#!/bin/sh

set -e

uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 &

exec streamlit run frontend/dashboard.py \
    --server.address=0.0.0.0 \
    --server.port="${PORT:-8501}"
