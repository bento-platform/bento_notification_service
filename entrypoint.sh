#!/bin/sh

cd bento_notification_service || exit
flask db upgrade
cd .. || exit

if [ -z "${INTERNAL_PORT}" ]; then
  # Set default internal port to 5000
  INTERNAL_PORT=5000
fi

# shellcheck disable=SC2003
# shellcheck disable=SC2046
gunicorn bento_notification_service.app:application \
  --workers 1 \
  --threads $(expr 2 \* $(nproc --all) + 1) \
  --bind "0.0.0.0:${INTERNAL_PORT}"
