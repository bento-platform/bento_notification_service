import uuid

from asgiref.sync import async_to_sync
from bento_lib.auth.permissions import P_VIEW_NOTIFICATIONS
from bento_lib.auth.resources import RESOURCE_EVERYTHING
from bento_lib.responses.flask_errors import flask_not_found_error
from bento_lib.service_info.constants import SERVICE_ORGANIZATION_C3G
from bento_lib.service_info.helpers import build_service_info
from flask import Blueprint, current_app, jsonify
from flask_sqlalchemy.session import Session
from pydantic import TypeAdapter
from sqlalchemy import select, update

from . import __version__
from .authz import authz_middleware
from .constants import BENTO_SERVICE_KIND, SERVICE_NAME, SERVICE_TYPE
from .db import db
from .logger import logger
from .models import Notification
from .pydantic_models import NotificationResponse

PERMISSION_SET_VIEW = frozenset({P_VIEW_NOTIFICATIONS})

notification_service = Blueprint("notification_service", __name__)

build_service_info_sync = async_to_sync(build_service_info)


class NotificationController:
    @staticmethod
    def get_notifications(session: Session) -> list[Notification]:
        return session.scalars(select(Notification)).all()

    @staticmethod
    def get_notification_by_id(session: Session, n_id: str | uuid.UUID) -> Notification | None:
        return session.scalars(select(Notification).where(Notification.id == str(n_id))).one_or_none()

    @staticmethod
    def mark_all_notifications_as_read(session: Session):
        session.execute(update(Notification).where(Notification._read == False).values(_read=True))
        session.commit()


notification_list_serializer = TypeAdapter(list[NotificationResponse])


@notification_service.route("/notifications", methods=["GET"])
@authz_middleware.deco_require_permissions_on_resource(PERMISSION_SET_VIEW, RESOURCE_EVERYTHING)
def notification_list():
    notifications = NotificationController.get_notifications(db.session)
    return jsonify(notification_list_serializer.dump_python([n.to_pydantic() for n in notifications], mode="json"))


@notification_service.route("/notifications/all-read", methods=["PUT"])
@authz_middleware.deco_require_permissions_on_resource(PERMISSION_SET_VIEW, RESOURCE_EVERYTHING)
def notification_all_read():
    NotificationController.mark_all_notifications_as_read(db.session)
    return current_app.response_class(status=204)


@notification_service.route("/notifications/<uuid:n_id>", methods=["GET"])
@authz_middleware.deco_require_permissions_on_resource(PERMISSION_SET_VIEW, RESOURCE_EVERYTHING)
def notification_detail(n_id: uuid.UUID):
    notification = NotificationController.get_notification_by_id(db.session, n_id)
    return (
        jsonify(notification.to_pydantic().model_dump(mode="json"))
        if notification
        else flask_not_found_error(f"Notification {n_id} not found")
    )


@notification_service.route("/notifications/<uuid:n_id>/read", methods=["PUT"])
@authz_middleware.deco_require_permissions_on_resource(PERMISSION_SET_VIEW, RESOURCE_EVERYTHING)
def notification_read(n_id: uuid.UUID):
    notification = NotificationController.get_notification_by_id(db.session, n_id)

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
