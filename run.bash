#!/bin/bash

export FLASK_APP='bento_notification_service.app:create_app()'

# Set default internal port to 5000
: "${INTERNAL_PORT:=5000}"

# Run migrations, if needed
flask db upgrade

# Start API server - explicitly 1 worker for now
# shellcheck disable=SC2003
# shellcheck disable=SC2046
uvicorn "${FLASK_APP}" \
  --interface wsgi \
  --workers 1 \
  --host 0.0.0.0 \
  --port "${INTERNAL_PORT}"
