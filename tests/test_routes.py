import chord_lib
from jsonschema import validate


def test_service_info(client):
    res = client.get("/service-info")
    data = res.get_json()

    validate(data, chord_lib.schemas.ga4gh.SERVICE_INFO_SCHEMA)


def test_get_notifications(client, notification):
    res = client.get("/notifications")
    data = res.get_json()

    assert res.status_code == 200
    assert len(data) == 1
    assert data[0]['title'] == notification.title
    assert data[0]['description'] == notification.description


def test_get_notification(client, notification):
    res = client.get(f"/notifications/{notification.id}")
    data = res.get_json()

    assert res.status_code == 200
    assert data['title'] == notification.title
    assert data['description'] == notification.description


def test_get_notification_fail(client):
    res = client.get(f"/notifications/123")
    data = res.get_json()

    assert res.status_code == 404


def test_notification_read(client, notification):
    assert notification.read == False

    res = client.put(f"/notifications/{notification.id}/read")
    data = res.get_json()

    assert res.status_code == 204

    res = client.get(f"/notifications/{notification.id}")
    data = res.get_json()

    assert res.status_code == 200
    assert data['read'] == True
