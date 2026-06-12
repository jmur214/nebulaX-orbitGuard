"""GET /events/recent — team filtering, exclusion, and limits."""

from conftest import make_event



async def seed(client):
    """Mixed-team event set used by the filtering tests."""
    events = [
        make_event(origin_module="red.attack.engine", event_type="EXPLOIT_SUCCESS", severity="CRITICAL"),
        make_event(origin_module="red.vuln.scanner", event_type="VULN_REPORT", severity="MEDIUM"),
        make_event(origin_module="blue.sentinel", event_type="THREAT_DETECTED", severity="HIGH"),
        make_event(origin_module="space.tracker", event_type="TLE_UPDATE", severity="INFO"),
        make_event(origin_module="space.tracker", event_type="SATELLITE_PASS", severity="INFO"),
    ]
    for e in events:
        resp = await client.post("/events/ingest", json=e)
        assert resp.status_code == 200


async def test_recent_returns_all_by_default(client):
    await seed(client)
    resp = await client.get("/events/recent")
    assert resp.status_code == 200
    assert len(resp.json()) == 5


async def test_recent_team_red_filter(client):
    await seed(client)
    resp = await client.get("/events/recent", params={"team": "red"})
    rows = resp.json()
    assert len(rows) == 2
    assert all(r["origin_module"].startswith("red.") for r in rows)


async def test_recent_team_blue_filter(client):
    await seed(client)
    resp = await client.get("/events/recent", params={"team": "blue"})
    rows = resp.json()
    assert len(rows) == 1
    assert rows[0]["event_type"] == "THREAT_DETECTED"


async def test_recent_team_space_filter(client):
    await seed(client)
    resp = await client.get("/events/recent", params={"team": "space"})
    rows = resp.json()
    assert len(rows) == 2
    assert all(r["origin_module"].startswith("space.") for r in rows)


async def test_recent_exclude_type(client):
    """The dashboard uses exclude_type=TLE_UPDATE to keep feeds readable."""
    await seed(client)
    resp = await client.get("/events/recent", params={"exclude_type": "TLE_UPDATE"})
    rows = resp.json()
    assert len(rows) == 4
    assert all(r["event_type"] != "TLE_UPDATE" for r in rows)


async def test_recent_respects_limit(client):
    await seed(client)
    resp = await client.get("/events/recent", params={"limit": 2})
    assert len(resp.json()) == 2
