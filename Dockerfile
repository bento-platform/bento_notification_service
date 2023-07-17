FROM ghcr.io/bento-platform/bento_base_image:python-debian-2023.05.12

# Run as root in the Dockerfile until we drop down to the service user in the entrypoint
USER root

RUN apt-get update -y && \
    apt-get install -y libpq-dev python-dev && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir gunicorn==20.1.0

WORKDIR /notification

# Create data directory
RUN mkdir -p /notification/data

COPY pyproject.toml .
COPY poetry.toml .
COPY poetry.lock .

# Install production dependencies
# Without --no-root, we get errors related to the code not being copied in yet.
# But we don't want the code here, otherwise Docker cache doesn't work well.
RUN poetry install --without dev --no-root

# Manually copy only what's relevant
# (Don't use .dockerignore, which allows us to have development containers too)
COPY bento_notification_service bento_notification_service
COPY entrypoint.bash .
COPY run.bash .
COPY LICENSE .
COPY README.md .
RUN ls /notification

# Install the module itself, locally (similar to `pip install -e .`)
RUN poetry install --without dev

# Run
#  - Must be ENTRYPOINT and not CMD since this needs root to fix permissions, after which it drops down via gosu
#  - CMD passes script to run after fixing up permissions with root and dropping down into the service user
ENTRYPOINT [ "bash", "./entrypoint.bash" ]
CMD [ "bash", "./run.bash" ]
