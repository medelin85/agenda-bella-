#!/bin/sh
set -eu
python prepare_production.py
exec gunicorn --workers 1 --threads 2 --bind "0.0.0.0:${PORT:-10000}" --error-logfile - 'agenda_bella:create_app()'
