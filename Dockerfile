FROM ghcr.io/bento-platform/bento_base_image:python-debian-2023.01.17

# TODO: change USER
USER root
RUN apt-get update -y && apt-get install -y libpq-dev python-dev

RUN pip install --no-cache-dir poetry==1.3.2 gunicorn==20.1.0

WORKDIR /notification

# Create data directory
RUN mkdir -p /notification/data

COPY pyproject.toml pyproject.toml
COPY poetry.toml poetry.toml
COPY poetry.lock poetry.lock

# Install production dependencies
# Without --no-root, we get errors related to the code not being copied in yet.
# But we don't want the code here, otherwise Docker cache doesn't work well.
RUN poetry install --without dev --no-root

# Manually copy only what's relevant
# (Don't use .dockerignore, which allows us to have development containers too)
COPY bento_notification_service bento_notification_service
COPY entrypoint.sh entrypoint.sh
COPY LICENSE LICENSE
COPY README.md README.md
RUN ls /notification

# Install the module itself, locally (similar to `pip install -e .`)
RUN poetry install --without dev

# Run
ENTRYPOINT [ "sh", "./entrypoint.sh" ]
