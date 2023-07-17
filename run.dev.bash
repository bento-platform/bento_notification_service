#!/bin/bash

# Update dependencies and install module locally
/poetry_user_install_dev.bash

# Update dependencies and install module locally (similar to pip install -e: "editable mode")
poetry install

export FLASK_ENV='development'
export FLASK_APP='bento_notification_service.app:create_app()'

# Set default internal port to 5000
: "${INTERNAL_PORT:=5000}"

# Run migrations, if needed
flask db upgrade

# Start Flask + debugger
python -m debugpy --listen 0.0.0.0:5678 -m flask run \
  --host 0.0.0.0 \
  --port "${INTERNAL_PORT}"
