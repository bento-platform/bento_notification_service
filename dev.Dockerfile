FROM ghcr.io/bento-platform/bento_base_image:python-debian-2022.10.11

# TODO: change USER
USER root
RUN apt-get update -y && apt-get install -y libpq-dev python-dev

RUN pip install --no-cache-dir poetry==1.2.2 "gunicorn==20.1.0"

WORKDIR /notification

# Create data directory
RUN mkdir -p /notification/data

COPY pyproject.toml pyproject.toml
COPY poetry.toml poetry.toml
COPY poetry.lock poetry.lock
COPY entrypoint.dev.sh entrypoint.dev.sh

# Install production + development dependencies
# Without --no-root, we get errors related to the code not being copied in yet.
# But we don't want the code here, otherwise Docker cache doesn't work well.
RUN poetry install --no-root

# Don't include actual code in the development image - will be mounted in using a volume.

CMD [ "sh", "./entrypoint.dev.sh" ]
