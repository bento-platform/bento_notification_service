import chord_notification_service
import os
import uuid

from chord_lib.events.types import EVENT_CREATE_NOTIFICATION, EVENT_NOTIFICATION
from flask import Flask, jsonify

from .db import *
from .events import *
from .notifications import notification_dict


SERVICE_ARTIFACT = "notification"
SERVICE_TYPE = "ca.c3g.chord:{}:{}".format(SERVICE_ARTIFACT, chord_notification_service.__version__)
SERVICE_ID = os.environ.get("SERVICE_ID", SERVICE_TYPE)


application = Flask(__name__)
application.config.from_mapping(
    DATABASE=os.environ.get("DATABASE", "chord_notification_service.db")
)

application.teardown_appcontext(close_db)

with application.app_context():
    if not os.path.exists(os.path.join(os.getcwd(), application.config["DATABASE"])):
        init_db()
    else:
        update_db()


    def event_handler(message):
        db = get_db()
        c = db.cursor()

        if message["type"] == EVENT_CREATE_NOTIFICATION:
            new_id = create_notification(db, c, message["data"]["title"], message["data"]["description"],
                                         message["data"]["action_type"], message["data"]["action_target"])
            if new_id:
                event_bus.publish_service_event(SERVICE_ARTIFACT, EVENT_NOTIFICATION, get_notification(c, new_id))

    event_bus.add_handler("chord.*", event_handler)
    event_bus.start_event_loop()


@application.route("/notifications", methods=["GET"])
def notification_list():
    c = get_db().cursor()
    c.execute("SELECT * FROM notifications")
    return jsonify([notification_dict(n) for n in c.fetchall()])


@application.route("/notifications/<int:notification_id>", methods=["GET"])
def notification_detail(notification_id: int):
    c = get_db().cursor()
    notification = get_notification(c, str(notification_id))
    return notification if notification is not None else application.response_class(status=404)


@application.route("/notifications/<uuid:notification_id>/read", methods=["POST"])
def notification_read(notification_id: uuid.UUID):
    db = get_db()
    c = db.cursor()

    notification = get_notification(c, str(notification_id))
    if notification is None:
        return application.response_class(status=404)

    c.execute("UPDATE notifications SET read = 1 WHERE id = ?", (str(notification_id),))
    db.commit()

    return application.response_class(status=201)


@application.route("/service-info", methods=["GET"])
def service_info():
    # Spec: https://github.com/ga4gh-discovery/ga4gh-service-info

    return jsonify({
        "id": SERVICE_ID,
        "name": "CHORD Notification Service",  # TODO: Should be globally unique?
        "type": SERVICE_TYPE,
        "description": "Notification service for a CHORD application.",
        "organization": {
            "name": "C3G",
            "url": "http://www.computationalgenomics.ca"
        },
        "contactUrl": "mailto:david.lougheed@mail.mcgill.ca",
        "version": chord_notification_service.__version__
    })
