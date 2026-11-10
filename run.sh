#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3}"
if [ -x ".venv/bin/python" ]; then
  PYTHON=".venv/bin/python"
fi

if ! "$PYTHON" -c "import django" >/dev/null 2>&1; then
  echo "Django not found; installing requirements..."
  "$PYTHON" -m pip install -r requirements.txt
fi

if [ ! -f "db.sqlite3" ]; then
  echo "First run: applying migrations and seeding demo content..."
  "$PYTHON" manage.py migrate
  "$PYTHON" manage.py seed_demo --with-admin
fi

echo "Starting IR 之下 at http://127.0.0.1:8000/"
exec "$PYTHON" manage.py runserver 127.0.0.1:8000
