import os

from chord_lib.auth.flask_decorators import flask_permissions_owner
from chord_lib.events.types import EVENT_CREATE_NOTIFICATION, EVENT_NOTIFICATION
from chord_lib.responses.flask_errors import *
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.exceptions import BadRequest, NotFound

from .config import APP_DIR, Config


MIGRATION_DIR = os.path.join(APP_DIR, "migrations")


application = Flask(__name__)
application.config.from_object(Config)

db = SQLAlchemy(application)
migrate = Migrate(application, db, directory=MIGRATION_DIR)

# Generic catch-all
application.register_error_handler(
    Exception, 
    flask_error_wrap_with_traceback(
        flask_internal_server_error,
        service_name=application.config['SERVICE_NAME']
    )
)
application.register_error_handler(BadRequest, flask_error_wrap(flask_bad_request_error))
application.register_error_handler(NotFound, flask_error_wrap(flask_not_found_error))


from chord_notification_service import routes, models  # noqa: E402,F401
