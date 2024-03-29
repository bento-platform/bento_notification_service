import bento_lib
from jsonschema import validate


def test_service_info(client):
    res = client.get("/service-info")
    data = res.get_json()

    validate(data, bento_lib.schemas.ga4gh.SERVICE_INFO_SCHEMA)


def test_get_notifications(client, notification):
    res = client.get("/notifications")
    data = res.get_json()

    assert res.status_code == 200
    assert len(data) == 1
    assert data[0]["title"] == notification.title
    assert data[0]["description"] == notification.description


def test_notifications_all_read(client, notification):
    assert notification.read is False

    res = client.put("/notifications/all-read")

    assert res.status_code == 204

    res = client.get(f"/notifications/{notification.id}")
    data = res.get_json()

    assert res.status_code == 200
    assert data["read"] is True


def test_get_notification(client, notification):
    res = client.get(f"/notifications/{notification.id}")
    data = res.get_json()

    assert res.status_code == 200
    assert data["title"] == notification.title
    assert data["description"] == notification.description


def test_get_notification_fail(client):
    res = client.get("/notifications/ca2c2063-e744-408b-b486-79d3a48ef179")

    assert res.status_code == 404


def test_notification_read(client, notification):
    assert notification.read is False

    res = client.put(f"/notifications/{notification.id}/read")

    assert res.status_code == 204

    res = client.get(f"/notifications/{notification.id}")
    data = res.get_json()

    assert res.status_code == 200
    assert data["read"] is True


def test_notification_read_fail(client):
    res = client.put("/notifications/ca2c2063-e744-408b-b486-79d3a48ef179/read")

    assert res.status_code == 404
