"""GET /satellite/orbit and the orbit_computer module."""
from datetime import datetime, timezone


from orbit_computer import compute_orbit_path, get_current_position
from conftest import make_event, ISS_TLE_LINE1, ISS_TLE_LINE2


FIXED_START = datetime(2024, 1, 23, 12, 0, 0, tzinfo=timezone.utc)


# ---------- orbit_computer unit tests (no app needed) ----------

def test_compute_orbit_path_shape():
    path = compute_orbit_path(
        ISS_TLE_LINE1, ISS_TLE_LINE2, "ISS", start_time=FIXED_START
    )
    # 90 min duration at 2-min intervals, inclusive of t=0 → 46 points
    assert len(path) == 46
    for lat, lon, alt in path:
        assert -90 <= lat <= 90
        assert -180 <= lon <= 180
        # ISS altitude ~370–460 km; generous bounds catch unit errors
        assert 300 < alt < 500


def test_compute_orbit_path_is_deterministic_with_fixed_start():
    a = compute_orbit_path(ISS_TLE_LINE1, ISS_TLE_LINE2, start_time=FIXED_START)
    b = compute_orbit_path(ISS_TLE_LINE1, ISS_TLE_LINE2, start_time=FIXED_START)
    assert a == b


def test_compute_orbit_path_custom_duration():
    path = compute_orbit_path(
        ISS_TLE_LINE1, ISS_TLE_LINE2,
        duration_minutes=30, interval_minutes=5, start_time=FIXED_START,
    )
    assert len(path) == 7  # 0,5,...,30


def test_compute_orbit_path_invalid_tle_returns_empty():
    assert compute_orbit_path("garbage", "also garbage") == []


def test_get_current_position_valid():
    pos = get_current_position(ISS_TLE_LINE1, ISS_TLE_LINE2)
    assert pos is not None
    assert -90 <= pos["lat"] <= 90
    assert -180 <= pos["lon"] <= 180


def test_get_current_position_invalid_tle():
    assert get_current_position("bad", "tle") is None


# ---------- /satellite/orbit endpoint tests ----------

async def ingest_tle(client, sat_name, line1=ISS_TLE_LINE1, line2=ISS_TLE_LINE2):
    body = make_event(
        event_type="TLE_UPDATE",
        origin_module="space.tracker",
        payload={
            "sat_name": sat_name,
            "norad_id": 25544,
            "tle": {"line1": line1, "line2": line2},
        },
    )
    resp = await client.post("/events/ingest", json=body)
    assert resp.status_code == 200


async def test_orbit_endpoint_happy_path(client):
    await ingest_tle(client, "ISS (ZARYA)")
    resp = await client.get("/satellite/orbit", params={"sat_name": "ISS (ZARYA)"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["sat_name"] == "ISS (ZARYA)"
    assert data["points"] == len(data["orbit_path"]) == 46
    assert data["source"] == "computed"  # no Redis in tests → no cache


async def test_orbit_endpoint_unknown_satellite_404(client):
    resp = await client.get("/satellite/orbit", params={"sat_name": "NO-SUCH-SAT"})
    assert resp.status_code == 404


async def test_orbit_endpoint_missing_tle_400(client):
    await ingest_tle(client, "BROKEN-SAT", line1="MISSING", line2="MISSING")
    resp = await client.get("/satellite/orbit", params={"sat_name": "BROKEN-SAT"})
    assert resp.status_code == 400


async def test_orbit_endpoint_uses_latest_tle_for_named_sat(client):
    """Two sats with TLEs — query must resolve by payload sat_name (JSON path)."""
    await ingest_tle(client, "SAT-A")
    await ingest_tle(client, "SAT-B")
    resp = await client.get("/satellite/orbit", params={"sat_name": "SAT-B"})
    assert resp.status_code == 200
    assert resp.json()["sat_name"] == "SAT-B"
