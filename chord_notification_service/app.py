import chord_notification_service
import os

from flask import Flask, jsonify

from .db import *


SERVICE_TYPE = "ca.c3g.chord:notification:{}".format(chord_notification_service.__version__)
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


def notification_dict(notification) -> dict:
    return {
        "id": notification[0],
        "title": notification[1],
        "description": notification[2],
        "action_type": notification[3],
        "action_target": notification[4],
        "read": bool(notification[5]),
    }


@application.route("/notifications", methods=["GET"])
def notification_list():
    c = get_db().cursor()
    c.execute("SELECT * FROM notifications")
    return jsonify([notification_dict(n) for n in c.fetchall()])


@application.route("/notifications/<int:notification_id>", methods=["GET"])
def notification_detail(notification_id: int):
    c = get_db().cursor()
    c.execute("SELECT * FROM notifications WHERE id = ?", (notification_id,))
    notification = c.fetchone()

    if notification is None:
        return application.response_class(status=404)

    return notification_dict(notification)


@application.route("/notifications/<int:notification_id>/read", methods=["POST"])
def notification_read(notification_id: int):
    db = get_db()
    c = db.cursor()

    c.execute("SELECT * FROM notifications WHERE id = ?", (notification_id,))
    if c.fetchone() is None:
        return application.response_class(status=404)

    c.execute("UPDATE notifications SET read = 1 WHERE id = ?", (notification_id,))
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
