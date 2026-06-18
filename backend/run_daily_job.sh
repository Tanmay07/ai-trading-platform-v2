#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
export PYTHONPATH=.
python scripts/daily_suggestion_job.py
