from bento_lib.responses.flask_errors import (
    flask_error_wrap,
    flask_error_wrap_with_traceback,
    flask_internal_server_error,
    flask_bad_request_error,
    flask_not_found_error
)
from flask import Flask
from flask_migrate import Migrate
from werkzeug.exceptions import BadRequest, NotFound

from .config import Config
from .constants import MIGRATION_DIR, SERVICE_NAME
from .db import db
from .events import start_event_bus
from .routes import notification_service


application = Flask(__name__)
application.config.from_object(Config)

# Initialize SQLAlchemy and migrate the database if necessary
db.init_app(application)
migrate = Migrate(application, db, directory=MIGRATION_DIR)

# Mount the application routes
application.register_blueprint(notification_service)

# Set up generic exception handlers, to give nicely formatted responses
#  - Generic catch-all
application.register_error_handler(
    Exception,
    flask_error_wrap_with_traceback(
        flask_internal_server_error,
        service_name=SERVICE_NAME
    )
)
application.register_error_handler(BadRequest, flask_error_wrap(flask_bad_request_error))
application.register_error_handler(NotFound, flask_error_wrap(flask_not_found_error))

# Start the event loop, or exit the service if Redis isn't available
with application.app_context():
    start_event_bus(application)
