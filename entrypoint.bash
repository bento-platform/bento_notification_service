#!/bin/bash

cd /notification || exit

# Create bento_user + home
source /create_service_user.bash

# Fix permissions on /notification, the database, and /env
chown -R bento_user:bento_user /notification
if [[ -n "${DATABASE}" ]]; then
  chown -R bento_user:bento_user "${DATABASE}"
  chmod -R o-rwx "${DATABASE}"  # Remove all access from others to the database
fi
if [[ -d /env ]]; then
  chown -R bento_user:bento_user /env
fi

# Configure git from entrypoint, since we've overwritten the base image entrypoint
gosu bento_user /bin/bash -c '/set_gitconfig.bash'

# Drop into bento_user from root and execute the CMD specified for the image
exec gosu bento_user "$@"
