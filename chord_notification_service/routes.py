import uuid
from chord_lib.auth.flask_decorators import flask_permissions_owner
from flask import jsonify
from .app import application, db
from .models import Notification


@application.route("/notifications", methods=["GET"])
@flask_permissions_owner
def notification_list():
    notifications = Notification.query.all()
    return jsonify([n.serialize for n in notifications])


@application.route("/notifications/<uuid:n_id>", methods=["GET"])
@flask_permissions_owner
def notification_detail(n_id: uuid.UUID):
    notification = Notification.query.filter_by(id=str(n_id)).first()
    return jsonify(notification.serialize) if notification else flask_not_found_error(f"Notification {n_id} not found")


@application.route("/notifications/<uuid:n_id>/read", methods=["PUT"])
@flask_permissions_owner
def notification_read(n_id: uuid.UUID):
    notification = Notification.query.filter_by(id=str(n_id)).first()

    if not notification:
        return flask_not_found_error(f"Notification {n_id} not found")

    notification.is_read()
    db.session.commit()

    return application.response_class(status=204)


@application.route("/service-info", methods=["GET"])
def service_info():
    # Spec: https://github.com/ga4gh-discovery/ga4gh-service-info

    return jsonify({
        "id": application.config['SERVICE_ID'],
        "name": application.config['SERVICE_NAME'],
        "type": application.config['SERVICE_TYPE'],
        "description": "Notification service for a CHORD application.",
        "organization": {
            "name": "C3G",
            "url": "http://www.computationalgenomics.ca"
        },
        "contactUrl": "mailto:david.lougheed@mail.mcgill.ca",
        "version": application.config['VERSION']
    })
