#!/bin/bash

# If set, use the local UID from outside the container (or default to 1000)
USER_ID=${BENTO_UID:-1000}

echo "[bento_notification_service] [entrypoint] starting with USER_ID=${USER_ID}"

# Create service user
useradd --shell /bin/bash -u "${USER_ID}" --non-unique -c "Bento container user" -m bento_user
export HOME=/home/bento_user

# Fix permissions on /notification
chown -R bento_user:bento_user /notification
chmod -R o-rwx /notification  # Remove all access from others

# Drop into bento_user from root and execute the CMD specified for the image
exec gosu bento_user "$@"
