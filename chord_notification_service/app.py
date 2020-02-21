import chord_notification_service
import os
import uuid

from chord_lib.auth.flask_decorators import flask_permissions_owner
from chord_lib.events.types import EVENT_CREATE_NOTIFICATION, EVENT_NOTIFICATION
from chord_lib.responses.flask_errors import *
from flask import Flask, jsonify
from werkzeug.exceptions import BadRequest, NotFound

from .db import *
from .events import *
from .notifications import notification_dict


SERVICE_ARTIFACT = "notification"
SERVICE_TYPE = "ca.c3g.chord:{}:{}".format(SERVICE_ARTIFACT, chord_notification_service.__version__)
SERVICE_ID = os.environ.get("SERVICE_ID", SERVICE_TYPE)
SERVICE_NAME = "CHORD Notification Service"


application = Flask(__name__)
application.teardown_appcontext(close_db)

# Generic catch-all
application.register_error_handler(Exception, flask_error_wrap_with_traceback(flask_internal_server_error,
                                                                              service_name=SERVICE_NAME))
application.register_error_handler(BadRequest, flask_error_wrap(flask_bad_request_error))
application.register_error_handler(NotFound, flask_error_wrap(flask_not_found_error))


with application.app_context():
    if not os.path.exists(os.path.join(os.getcwd(), DATABASE)):
        init_db()
    else:
        update_db()


def event_handler(message):
    db = get_new_db_connection()  # TODO: Wasteful
    c = db.cursor()

    event = message["data"]
    if event["type"] == EVENT_CREATE_NOTIFICATION:
        new_id = create_notification(db, c, event["data"]["title"], event["data"]["description"],
                                     event["data"]["notification_type"], event["data"]["action_target"])
        if new_id:
            event_bus.publish_service_event(SERVICE_ARTIFACT, EVENT_NOTIFICATION, get_notification(c, new_id))

    db.close()


event_bus.add_handler("chord.*", event_handler)
event_bus.start_event_loop()


@application.route("/notifications", methods=["GET"])
@flask_permissions_owner
def notification_list():
    c = get_db().cursor()
    c.execute("SELECT * FROM notifications")
    return jsonify([notification_dict(n) for n in c.fetchall()])


@application.route("/notifications/<uuid:n_id>", methods=["GET"])
@flask_permissions_owner
def notification_detail(n_id: uuid.UUID):
    c = get_db().cursor()
    notification = get_notification(c, str(n_id))
    return notification if notification is not None else flask_not_found_error(f"Notification {n_id} not found")


@application.route("/notifications/<uuid:n_id>/read", methods=["POST"])
@flask_permissions_owner
def notification_read(n_id: uuid.UUID):
    db = get_db()
    c = db.cursor()

    notification = get_notification(c, str(n_id))
    if notification is None:
        return flask_not_found_error(f"Notification {n_id} not found")

    c.execute("UPDATE notifications SET read = 1 WHERE id = ?", (str(n_id),))
    db.commit()

    return application.response_class(status=204)


@application.route("/service-info", methods=["GET"])
def service_info():
    # Spec: https://github.com/ga4gh-discovery/ga4gh-service-info

    return jsonify({
        "id": SERVICE_ID,
        "name": SERVICE_NAME,
        "type": SERVICE_TYPE,
        "description": "Notification service for a CHORD application.",
        "organization": {
            "name": "C3G",
            "url": "http://www.computationalgenomics.ca"
        },
        "contactUrl": "mailto:david.lougheed@mail.mcgill.ca",
        "version": chord_notification_service.__version__
    })
