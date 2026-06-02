#!/usr/bin/env bash
# Build script for deploying CareerPath on Render (or any similar PaaS).
set -o errexit

# Install Python dependencies.
pip install -r requirements.txt

# Install the spaCy English model used by the resume parser.
python -m spacy download en_core_web_sm || \
  pip install "https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl"

# Collect static assets for WhiteNoise to serve.
python manage.py collectstatic --no-input

# Apply database migrations.
python manage.py migrate

# Load the bundled CSV datasets so all features work on a fresh database.
python manage.py seed_data
