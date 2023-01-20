#!/bin/sh

export FLASK_ENV='development'
export FLASK_APP='bento_notification_service.app:create_app()'

if [ -z "${INTERNAL_PORT}" ]; then
  # Set default internal port to 5000
  INTERNAL_PORT=5000
fi

# Install module locally (similar to pip install -e: "editable mode")
poetry install

# Run migrations, if needed
flask db upgrade

# Start Flask + debugger
python -m debugpy --listen 0.0.0.0:5678 -m flask run --host 0.0.0.0 --port "${INTERNAL_PORT}"
