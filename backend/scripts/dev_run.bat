@echo off
REM Development server startup script for Windows

set PYTHONPATH=.
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
