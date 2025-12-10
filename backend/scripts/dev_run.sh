#!/usr/bin/env bash
# Development server startup script

export PYTHONPATH=.
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
