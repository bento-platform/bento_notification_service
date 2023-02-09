FROM ghcr.io/bento-platform/bento_base_image:python-debian-2023.02.09

# TODO: change USER
USER root
RUN apt-get update -y && apt-get install -y libpq-dev python-dev

RUN pip install --no-cache-dir poetry==1.3.2 "gunicorn==20.1.0"

WORKDIR /notification

# Create data directory
RUN mkdir -p /notification/data

COPY pyproject.toml .
COPY poetry.toml .
COPY poetry.lock .
COPY entrypoint.dev.bash .

# Install production + development dependencies
# Without --no-root, we get errors related to the code not being copied in yet.
# But we don't want the code here, otherwise Docker cache doesn't work well.
RUN poetry install --no-root

# Don't include actual code in the development image - will be mounted in using a volume.

CMD [ "bash", "./entrypoint.dev.bash" ]
