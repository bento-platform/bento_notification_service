#!/bin/sh

export FLASK_APP='bento_notification_service.app:create_app()'

if [ -z "${INTERNAL_PORT}" ]; then
  # Set default internal port to 5000
  INTERNAL_PORT=5000
fi

# Run migrations, if needed
flask db upgrade

# Start API server - explicitly 1 worker for now
# shellcheck disable=SC2003
# shellcheck disable=SC2046
gunicorn "${FLASK_APP}" \
  --workers 1 \
  --bind "0.0.0.0:${INTERNAL_PORT}"
