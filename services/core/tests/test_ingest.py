"""POST /events/ingest — validation and persistence."""
from sqlalchemy import select, func

from db.models import EventModel
from conftest import make_event



async def test_health_check(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "online"


async def test_ingest_valid_event_persists(client, db_session):
    body = make_event(
        event_type="THREAT_DETECTED",
        origin_module="blue.sentinel",
        severity="HIGH",
        payload={"rule": "SSH brute force", "count": 14},
        context={"related_ip": "172.18.0.9", "mitre_attack_id": "T1110"},
    )
    resp = await client.post("/events/ingest", json=body)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "persisted"
    assert data["db_record"] == "created"

    # Verify the row actually landed with fields intact
    row = (await db_session.execute(select(EventModel))).scalar_one()
    assert row.event_type == "THREAT_DETECTED"
    assert row.origin_module == "blue.sentinel"
    assert row.severity == "HIGH"
    assert row.payload == {"rule": "SSH brute force", "count": 14}
    assert row.context["related_ip"] == "172.18.0.9"


async def test_ingest_rejects_unknown_event_type(client):
    body = make_event(event_type="NOT_A_REAL_TYPE")
    resp = await client.post("/events/ingest", json=body)
    assert resp.status_code == 422  # pydantic enum validation


async def test_ingest_rejects_unknown_severity(client):
    body = make_event(severity="APOCALYPTIC")
    resp = await client.post("/events/ingest", json=body)
    assert resp.status_code == 422


async def test_ingest_rejects_missing_meta(client):
    resp = await client.post(
        "/events/ingest", json={"context": {}, "payload": {}}
    )
    assert resp.status_code == 422


async def test_ingest_defaults_id_and_timestamp(client, db_session):
    """id/timestamp are server-defaulted when the producer omits them."""
    body = make_event()
    assert "id" not in body["event_meta"]
    resp = await client.post("/events/ingest", json=body)
    assert resp.status_code == 200

    row = (await db_session.execute(select(EventModel))).scalar_one()
    assert row.id is not None
    assert row.timestamp is not None


async def test_ingest_many_events_counted(client, db_session):
    for i in range(5):
        resp = await client.post(
            "/events/ingest", json=make_event(payload={"seq": i})
        )
        assert resp.status_code == 200
    count = (await db_session.execute(select(func.count(EventModel.id)))).scalar()
    assert count == 5
