import bento_lib
from jsonschema import validate


async def test_service_info(client):
    res = await client.get("/service-info")
    data = res.json()

    validate(data, bento_lib.schemas.ga4gh.SERVICE_INFO_SCHEMA)


async def test_get_notifications(client, notification):
    res = await client.get("/notifications")
    data = res.json()

    assert res.status_code == 200
    assert len(data) == 1
    assert data[0]["title"] == notification.title
    assert data[0]["description"] == notification.description


async def test_notifications_all_read(client, notification):
    assert notification.read is False

    res = await client.put("/notifications/all-read")

    assert res.status_code == 204

    res = await client.get(f"/notifications/{notification.id}")
    data = res.json()

    assert res.status_code == 200
    assert data["read"] is True


async def test_get_notification(client, notification):
    res = await client.get(f"/notifications/{notification.id}")
    data = res.json()

    assert res.status_code == 200
    assert data["title"] == notification.title
    assert data["description"] == notification.description


async def test_get_notification_fail(client):
    res = await client.get("/notifications/ca2c2063-e744-408b-b486-79d3a48ef179")

    assert res.status_code == 404


async def test_notification_read(client, notification):
    assert notification.read is False

    res = await client.put(f"/notifications/{notification.id}/read")

    assert res.status_code == 204

    res = await client.get(f"/notifications/{notification.id}")
    data = res.json()

    assert res.status_code == 200
    assert data["read"] is True


async def test_notification_read_fail(client):
    res = await client.put("/notifications/ca2c2063-e744-408b-b486-79d3a48ef179/read")

    assert res.status_code == 404


async def test_notification_bad_uuid(client):
    # Bento's FastAPI exception handlers turn validation errors into 400s
    res = await client.get("/notifications/not-a-uuid")

    assert res.status_code == 400
    assert res.json()["code"] == 400
