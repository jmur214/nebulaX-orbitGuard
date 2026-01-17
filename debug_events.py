import requests
import datetime
import uuid

CORE_API_URL = "http://localhost:8000/events/ingest"

event = {
    "event_meta": {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "origin_module": "red.debug.script",
        "event_type": "EXPLOIT_SUCCESS",
        "severity": "HIGH",
        "classification": "SIMULATION"
    },
    "context": {
        "mitre_attack_id": "T1234",
        "related_asset_id": "DEBUG-HOST"
    },
    "payload": {
        "details": "This is a test event from the debug script."
    }
}

try:
    print(f"Sending event to {CORE_API_URL}...")
    resp = requests.post(CORE_API_URL, json=event)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")
except Exception as e:
    print(f"Failed: {e}")
