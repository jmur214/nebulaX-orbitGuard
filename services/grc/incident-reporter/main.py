import time
import os
import random
import requests

# CONFIGURATION
CORE_HOST = os.getenv("CORE_HOST", "nebulax-core")
CORE_API_URL = f"http://{CORE_HOST}:8000/events/ingest"

print(" [ GRC ] Incident Reporter Online")
print(" [ GRC ] Generating PDF Reports...")

def simulate_reporting():
    if random.random() < 0.4: # 40% chance (increased for visibility)
        event = {
            "event_meta": {
                "event_type": "INFO",
                "origin_module": "grc.incident-reporter",
                "severity": "INFO",
                "classification": "SIMULATION"
            },
            "context": {},
            "payload": {
                "report_id": f"RPT-{random.randint(1000,9999)}",
                "status": "GENERATED",
                "recipients": ["ciso@nebulax.io"]
            }
        }
        try:
            requests.post(CORE_API_URL, json=event, timeout=10)
            print(" [ GRC ] Incident Report Generated")
        except Exception as e:
            print(f" [ GRC ] Error: {e}")

while True:
    simulate_reporting()
    time.sleep(45)
