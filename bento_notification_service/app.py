from bento_lib.responses.flask_errors import (
    flask_error_wrap,
    flask_error_wrap_with_traceback,
    flask_internal_server_error,
    flask_bad_request_error,
    flask_forbidden_error,
    flask_not_found_error
)
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from werkzeug.exceptions import BadRequest, Forbidden, NotFound

from .authz import authz_middleware
from .config import Config
from .constants import MIGRATION_DIR, SERVICE_NAME
from .db import db
from .events import start_event_bus
from .routes import notification_service


def create_app() -> Flask:
    application = Flask(__name__)
    application.config.from_object(Config)

    # Set up CORS
    CORS(application, origins=Config.CORS_ORIGINS)

    # Attach authorization middleware to application
    authz_middleware.attach(application)

    # Initialize SQLAlchemy and migrate the database if necessary
    db.init_app(application)
    Migrate(application, db, directory=MIGRATION_DIR)

    # Mount the application routes
    application.register_blueprint(notification_service)

    # Set up generic exception handlers, to give nicely formatted responses
    #  - Generic catch-all
    application.register_error_handler(
        Exception,
        flask_error_wrap_with_traceback(
            flask_internal_server_error,
            authz=authz_middleware,
            service_name=SERVICE_NAME,
        )
    )
    #  - Specific errors
    application.register_error_handler(BadRequest, flask_error_wrap(flask_bad_request_error, authz=authz_middleware))
    application.register_error_handler(Forbidden, flask_error_wrap(flask_forbidden_error, authz=authz_middleware))
    application.register_error_handler(NotFound, flask_error_wrap(flask_not_found_error, authz=authz_middleware))

    # Start the event loop, or exit the service if Redis isn't available
    with application.app_context():
        start_event_bus(application)

    return application
