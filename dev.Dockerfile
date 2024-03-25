FROM ghcr.io/bento-platform/bento_base_image:python-debian-2024.03.01

SHELL ["/bin/bash", "-c"]

# Run as root in the Dockerfile until we drop down to the service user in the entrypoint
USER root

RUN pip install --no-cache-dir gunicorn==21.2.0

WORKDIR /notification

# Create data directory
RUN mkdir -p /notification/data

COPY pyproject.toml .
COPY poetry.lock .
COPY entrypoint.bash .
COPY run.dev.bash .

# Install production + development dependencies
# Without --no-root, we get errors related to the code not being copied in yet.
# But we don't want the code here, otherwise Docker cache doesn't work well.
RUN poetry config virtualenvs.create false && \
    poetry install --no-root

# Don't include actual code in the development image - will be mounted in using a volume.

# Run
#  - Must be ENTRYPOINT and not CMD since this needs root to fix permissions, after which it drops down via gosu
#  - CMD passes script to run after fixing up permissions with root and dropping down into the service user
ENTRYPOINT [ "bash", "./entrypoint.bash" ]
CMD [ "bash", "./run.dev.bash" ]
