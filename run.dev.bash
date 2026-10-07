#!/bin/bash

# Update dependencies and install module locally
/poetry_user_install_dev.bash

# Update dependencies and install module locally (similar to pip install -e: "editable mode")
poetry install

# Set default internal port to 5000
: "${INTERNAL_PORT:=5000}"

# Set internal debug port, falling back to default in a Bento deployment
: "${DEBUGGER_PORT:=5681}"

# Run migrations, if needed
alembic upgrade head

# Start API server + debugger, with auto-reload on code changes
python -m debugpy --listen "0.0.0.0:${DEBUGGER_PORT}" -m uvicorn \
  --factory bento_notification_service.app:create_app \
  --host 0.0.0.0 \
  --port "${INTERNAL_PORT}" \
  --reload
