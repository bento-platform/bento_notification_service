import chord_notification_service
import os

from flask import Flask, jsonify


SERVICE_TYPE = "ca.c3g.chord:notification:{}".format(chord_notification_service.__version__)
SERVICE_ID = os.environ.get("SERVICE_ID", SERVICE_TYPE)


application = Flask(__name__)
application.config.from_mapping(
    DATABASE=os.environ.get("DATABASE", "chord_notification_service.db")
)


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
