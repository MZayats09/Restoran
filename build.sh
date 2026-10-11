#!/usr/bin/env bash
# Render виконує цей скрипт автоматично як Build Command (прописано в render.yaml).
# Нічого руками запускати не потрібно.
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
