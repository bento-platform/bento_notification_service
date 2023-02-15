import subprocess
import uuid

from bento_lib.auth.flask_decorators import flask_permissions_owner
from bento_lib.responses.flask_errors import flask_not_found_error
from flask import Blueprint, current_app, jsonify

from bento_notification_service import __version__
from .db import db
from .constants import BENTO_SERVICE_KIND, SERVICE_NAME, SERVICE_TYPE, ORG_C3G
from .models import Notification


notification_service = Blueprint("notification_service", __name__)


@notification_service.route("/notifications", methods=["GET"])
@flask_permissions_owner
def notification_list():
    notifications = Notification.query.all()
    return jsonify([n.serialize for n in notifications])


@notification_service.route("/notifications/all-read", methods=["PUT"])
@flask_permissions_owner
def notification_all_read():
    # TODO: This is slow/non-optimal but we shouldn't have enough notifications for it to matter.
    #  Ideally, it would be done using a bulk update query.

    for notification in Notification.query.filter_by(_read=False):
        notification.is_read()

    db.session.commit()

    return current_app.response_class(status=204)


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
    bento_debug = current_app.config["BENTO_DEBUG"]

    # Spec: https://github.com/ga4gh-discovery/ga4gh-service-info
    info = {
        "id": current_app.config["SERVICE_ID"],
        "name": SERVICE_NAME,
        "type": SERVICE_TYPE,
        "description": "Notification service for a Bento platform node.",
        "organization": ORG_C3G,
        "contactUrl": "mailto:info@c3g.ca",
        "version": __version__,
        "environment": "dev" if bento_debug else "prod",
        "bento": {
            "serviceKind": BENTO_SERVICE_KIND,
        },
    }

    if not bento_debug:
        return jsonify(info)

    try:
        if res_tag := subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"]):
            res_tag_str = res_tag.decode().rstrip()
            # noinspection PyTypeChecker
            info["bento"]["gitTag"] = res_tag_str
        if res_branch := subprocess.check_output(["git", "branch", "--show-current"]):
            res_branch_str = res_branch.decode().rstrip()
            # noinspection PyTypeChecker
            info["bento"]["gitBranch"] = res_branch_str
        if res_commit := subprocess.check_output(["git", "rev-parse", "HEAD"]):
            res_commit_str = res_commit.decode().rstrip()
            # noinspection PyTypeChecker
            info["bento"]["gitCommit"] = res_commit_str
    except Exception as e:
        except_name = type(e).__name__
        current_app.logger.info(f"Could not retrieve git information: {str(except_name)}: {e}")

    return jsonify(info)
