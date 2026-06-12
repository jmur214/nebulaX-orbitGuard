"""GET /game/state — scoring rules and DEFCON thresholds.

These tests pin the *current* core-api scoring behavior so the Phase 2
DEFCON/scoring reconciliation (see docs/ROADMAP.md) has a safety net and any
intentional change shows up as an explicit test update.
"""
import pytest

from conftest import make_event



async def ingest_n(client, event_type, n, origin="test.seed"):
    for _ in range(n):
        resp = await client.post(
            "/events/ingest",
            json=make_event(event_type=event_type, origin_module=origin),
        )
        assert resp.status_code == 200


async def test_empty_db_is_peace(client):
    resp = await client.get("/game/state")
    assert resp.status_code == 200
    state = resp.json()
    assert state == {
        "defcon": 5,
        "red_score": 0,
        "blue_score": 0,
        "status": "PEACE",
    }


async def test_red_scoring_rules(client):
    # 1×EXPLOIT_SUCCESS(50) + 2×CREDENTIAL_CRACKED(30) + 3×VULN_REPORT(10) = 140
    await ingest_n(client, "EXPLOIT_SUCCESS", 1)
    await ingest_n(client, "CREDENTIAL_CRACKED", 2)
    await ingest_n(client, "VULN_REPORT", 3)

    state = (await client.get("/game/state")).json()
    assert state["red_score"] == 140
    assert state["status"] == "ACTIVE_CONFLICT"


async def test_blue_scoring_rules(client):
    # 2×THREAT_DETECTED(20) + 3×AUTH_FAILURE(5) + 1×COMMAND_EXECUTED(2) = 57
    await ingest_n(client, "THREAT_DETECTED", 2)
    await ingest_n(client, "AUTH_FAILURE", 3)
    await ingest_n(client, "COMMAND_EXECUTED", 1)

    state = (await client.get("/game/state")).json()
    assert state["blue_score"] == 57
    # No red events → red score 0 → PEACE
    assert state["red_score"] == 0
    assert state["status"] == "PEACE"


@pytest.mark.parametrize(
    "exploit_count,expected_defcon",
    [
        (1, 5),   # 50 pts  → DEFCON 5
        (3, 4),   # 150 pts → >100 → DEFCON 4
        (7, 3),   # 350 pts → >300 → DEFCON 3
        (11, 2),  # 550 pts → >500 → DEFCON 2
        (21, 1),  # 1050 pts → >1000 → DEFCON 1
    ],
)
async def test_defcon_thresholds(client, exploit_count, expected_defcon):
    await ingest_n(client, "EXPLOIT_SUCCESS", exploit_count)
    state = (await client.get("/game/state")).json()
    assert state["red_score"] == exploit_count * 50
    assert state["defcon"] == expected_defcon
