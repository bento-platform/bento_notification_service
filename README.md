# Bento Notification Service

![Build Status](https://api.travis-ci.com/bento-platform/bento_notification_service.svg?branch=master)
[![codecov](https://codecov.io/gh/bento-platform/bento_notification_service/branch/master/graph/badge.svg)](https://codecov.io/gh/bento-platform/bento_notification_service)

Notification service for the Bento platform.

## Running in Development

Development dependencies are described in `requirements.txt` and can be
installed using the following command:

```bash
pip install -r requirements.txt
```

Afterwards we need to setup the DB:

```bash
flask db upgrade
```
