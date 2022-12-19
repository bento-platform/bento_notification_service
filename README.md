# Bento Notification Service

![Build Status](https://api.travis-ci.com/bento-platform/bento_notification_service.svg?branch=master)
[![codecov](https://codecov.io/gh/bento-platform/bento_notification_service/branch/master/graph/badge.svg)](https://codecov.io/gh/bento-platform/bento_notification_service)

Notification service for the Bento platform.


## Configuration

The Bento notification service is configured via environment variables

 * `DATABASE`: (*Misleadingly named*) Path to the **directory** in which the 
   `db.sqlite3` file can be found or created.
 * `REDIS_HOST`: Redis server host. Default: `localhost`
 * `REDIS_PORT`: Redis server port. Default: `6379`


## Running in Development

First, Poetry must be installed:
```
pip install poetry
```

Development dependencies are described in `pyproject.toml` using Poetry, and can be
installed using the following command:

```bash
poetry install
```

Afterwards we need to set up the DB:

```bash
flask db upgrade
```
