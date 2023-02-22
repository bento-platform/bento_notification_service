#!/bin/bash

cd /notification || exit

# Create bento_user + home
source /create_service_user.bash

# Fix permissions on /notification and /env
chown -R bento_user:bento_user /notification /env
if [[ -n "${DATABASE}" ]]; then
  chmod -R o-rwx "${DATABASE}"  # Remove all access from others to the database
fi

# Drop into bento_user from root and execute the CMD specified for the image
exec gosu bento_user "$@"
