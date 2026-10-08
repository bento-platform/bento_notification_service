#!/bin/bash

# Set default internal port to 5000
: "${INTERNAL_PORT:=5000}"

# Run migrations, if needed
alembic upgrade head

# Start API server - explicitly 1 worker for now
exec uvicorn \
  --factory bento_notification_service.app:create_app \
  --host 0.0.0.0 \
  --port "${INTERNAL_PORT}" \
  --workers 1 \
  --proxy-headers
