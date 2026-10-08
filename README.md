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
 * `BENTO_AUTHZ_SERVICE_URL`: Bento authorization service URL. Required unless authorization is disabled.
 * `BENTO_AUTHZ_ENABLED` (legacy name: `AUTHZ_ENABLED`): Whether to enforce authorization. Default: `true`
 * `CORS_ORIGINS`: Semicolon-separated list of allowed CORS origins.

Other standard Bento service variables (`BENTO_DEBUG`, `BENTO_CONTAINER_LOCAL`, `SERVICE_ID`, etc.) are defined by
`bento_lib.config.pydantic.BentoFastAPIBaseConfig`.


## Running in Development

First, Poetry `>=2.2.1,<3` must be installed:
```
pip install -U 'poetry>=2.2.1,<3'
```

Development dependencies are described in `pyproject.toml` using Poetry, and can be
installed using the following command:

```bash
poetry install
```

Afterward, we need to set up the DB (Alembic migrations; the DB location comes from the `DATABASE` variable):

```bash
poetry run alembic upgrade head
```

To create migrations, make sure your database is on the latest migration. Then, do the following:

```bash
poetry run alembic revision --autogenerate -m "Some message here"
```

To run the service (FastAPI, via uvicorn) locally:

```bash
poetry run uvicorn --factory bento_notification_service.app:create_app --port 5000 --reload
```


## Testing

To test locally, run:

```bash
poetry run tox
```
