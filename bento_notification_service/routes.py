import uuid
from bento_lib.auth.flask_decorators import flask_permissions_owner
from bento_lib.responses.flask_errors import flask_not_found_error
from flask import Blueprint, current_app, jsonify
from .app import db
from .models import Notification


notification_service = Blueprint("notification_service", __name__)


@notification_service.route("/notifications", methods=["GET"])
@flask_permissions_owner
def notification_list():
    notifications = Notification.query.all()
    return jsonify([n.serialize for n in notifications])


@notification_service.route("/notifications/<uuid:n_id>", methods=["GET"])
@flask_permissions_owner
def notification_detail(n_id: uuid.UUID):
    notification = Notification.query.filter_by(id=str(n_id)).first()
    return jsonify(notification.serialize) if notification else flask_not_found_error(f"Notification {n_id} not found")


@notification_service.route("/notifications/<uuid:n_id>/read", methods=["PUT"])
@flask_permissions_owner
def notification_read(n_id: uuid.UUID):
    notification = Notification.query.filter_by(id=str(n_id)).first()

    if not notification:
        return flask_not_found_error(f"Notification {n_id} not found")

    notification.is_read()
    db.session.commit()

    return current_app.response_class(status=204)


@notification_service.route("/service-info", methods=["GET"])
def service_info():
    # Spec: https://github.com/ga4gh-discovery/ga4gh-service-info

    return jsonify({
        "id": current_app.config['SERVICE_ID'],
        "name": current_app.config['SERVICE_NAME'],
        "type": current_app.config['SERVICE_TYPE'],
        "description": "Notification service for a Bento platform node.",
        "organization": {
            "name": "C3G",
            "url": "http://www.computationalgenomics.ca"
        },
        "contactUrl": "mailto:david.lougheed@mail.mcgill.ca",
        "version": current_app.config['VERSION']
    })
