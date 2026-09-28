#!/usr/bin/env bash
# build.sh — runs on every deploy

set -o errexit   # exit on error

pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate --noinput

# Optional — create a superuser on first deploy
# python manage.py createsuperuser --noinput || true