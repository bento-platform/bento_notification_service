# Bento Notification Service

![Build Status](https://api.travis-ci.com/bento-platform/bento_notification_service.svg?branch=master)
[![codecov](https://codecov.io/gh/bento-platform/bento_notification_service/branch/master/graph/badge.svg)](https://codecov.io/gh/bento-platform/bento_notification_service)

Notification service for the Bento platform.


## Configuration

The Bento notification service is configured via environment variables

 * `DATABASE`: (*Misleadingly named*) Path to the **directory** in which the 
   `db.sqlite3` file can be found or created.
 * `REDIS_SOCKET`: Path to Redis socket file, if using UNIX sockets for the 
   Redis connection. If set, all other `REDIS_*` environment variables (for 
   connecting to Redis via URL) will be ignored in this application.
 * `REDIS_HOST`: Redis server host. If `REDIS_SOCKET` is set, this will be 
    ignored. Default: `localhost`
 * `REDIS_PORT`: Redis server port. If `REDIS_SOCKET` is set, this will be 
    ignored. Default: `6379`


## Running in Development

Development dependencies are described in `requirements.txt` and can be
installed using the following command:

```bash
pip install -r requirements.txt
```

Afterwards we need to set up the DB:

```bash
flask db upgrade
```
