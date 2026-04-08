import time
import os
import random
import requests
import json
from datetime import datetime

# CONFIGURATION
CORE_HOST = os.getenv("CORE_HOST", "nebulax-core")
CORE_API_URL = f"http://{CORE_HOST}:8000/events/ingest"

print(" [ GRC ] Policy Mapper Online")
print(" [ GRC ] Mapping Alerts to Frameworks (GDPR, NIST, CFAA)...")

def simulate_mapping():
    if random.random() < 0.4: # 40% chance (increased for visibility)
        event = {
            "event_meta": {
                "event_type": "INFO",
                "origin_module": "grc.policy-mapper",
                "severity": "INFO",
                "classification": "SIMULATION"
            },
            "context": {
                "legal_compliance_tag": "GDPR-Art-33"
            },
            "payload": {
                "mapped_alert_id": str(random.randint(10000, 99999)),
                "framework": "GDPR",
                "violation": "Data Breach Notification"
            }
        }
        try:
            requests.post(CORE_API_URL, json=event, timeout=10)
            print(" [ GRC ] Policy Violation Mapped")
        except Exception as e:
            print(f" [ GRC ] Error: {e}")

while True:
    simulate_mapping()
    time.sleep(30)
