#!/usr/bin/env bash
# Render build command: ./build.sh
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py makemigrations accounts --no-input
python manage.py migrate --no-input
python manage.py setup_groups

# Optional: create an admin automatically (free plan has no shell).
# Set DJANGO_SUPERUSER_USERNAME / _EMAIL / _PASSWORD in Render > Environment.
if [[ -n "${DJANGO_SUPERUSER_USERNAME:-}" && -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]]; then
  python manage.py createsuperuser --no-input || true
fi
