import uuid

from asgiref.sync import async_to_sync
from bento_lib.auth.permissions import P_VIEW_NOTIFICATIONS
from bento_lib.auth.resources import RESOURCE_EVERYTHING
from bento_lib.responses.flask_errors import flask_not_found_error
from bento_lib.service_info.constants import SERVICE_ORGANIZATION_C3G
from bento_lib.service_info.helpers import build_service_info
from flask import Blueprint, current_app, jsonify

from . import __version__
from .authz import authz_middleware
from .db import db
from .constants import BENTO_SERVICE_KIND, SERVICE_NAME, SERVICE_TYPE
from .logger import logger
from .models import Notification


PERMISSION_SET_VIEW = frozenset({P_VIEW_NOTIFICATIONS})

notification_service = Blueprint("notification_service", __name__)

build_service_info_sync = async_to_sync(build_service_info)


@notification_service.route("/notifications", methods=["GET"])
@authz_middleware.deco_require_permissions_on_resource(PERMISSION_SET_VIEW, RESOURCE_EVERYTHING)
def notification_list():
    notifications = Notification.query.all()
    return jsonify([n.serialize for n in notifications])


@notification_service.route("/notifications/all-read", methods=["PUT"])
@authz_middleware.deco_require_permissions_on_resource(PERMISSION_SET_VIEW, RESOURCE_EVERYTHING)
def notification_all_read():
    # TODO: This is slow/non-optimal but we shouldn't have enough notifications for it to matter.
    #  Ideally, it would be done using a bulk update query.

    for notification in Notification.query.filter_by(_read=False):
        notification.is_read()

    db.session.commit()

    return current_app.response_class(status=204)


@notification_service.route("/notifications/<uuid:n_id>", methods=["GET"])
@authz_middleware.deco_require_permissions_on_resource(PERMISSION_SET_VIEW, RESOURCE_EVERYTHING)
def notification_detail(n_id: uuid.UUID):
    notification = Notification.query.filter_by(id=str(n_id)).first()
    return jsonify(notification.serialize) if notification else flask_not_found_error(f"Notification {n_id} not found")


@notification_service.route("/notifications/<uuid:n_id>/read", methods=["PUT"])
@authz_middleware.deco_require_permissions_on_resource(PERMISSION_SET_VIEW, RESOURCE_EVERYTHING)
def notification_read(n_id: uuid.UUID):
    notification = Notification.query.filter_by(id=str(n_id)).first()

    if not notification:
        return flask_not_found_error(f"Notification {n_id} not found")

    notification.is_read()
    db.session.commit()

    return current_app.response_class(status=204)


@notification_service.route("/service-info", methods=["GET"])
@authz_middleware.deco_public_endpoint
def service_info():
    return build_service_info_sync(
        {
            "id": current_app.config["SERVICE_ID"],
            "name": SERVICE_NAME,
            "type": SERVICE_TYPE,
            "description": "Notification service for a Bento platform node.",
            "organization": SERVICE_ORGANIZATION_C3G,
            "contactUrl": "mailto:info@c3g.ca",
            "version": __version__,
            "bento": {
                "serviceKind": BENTO_SERVICE_KIND,
                "gitRepository": "https://github.com/bento-platform/bento_notification_service",
            },
        },
        debug=current_app.config["BENTO_DEBUG"],
        local=current_app.config["BENTO_CONTAINER_LOCAL"],
        logger=logger,
    )
