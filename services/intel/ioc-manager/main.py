import time
import os
import random
import requests
import json
from datetime import datetime

# CONFIGURATION
CORE_HOST = os.getenv("CORE_HOST", "nebulax-core")
CORE_API_URL = f"http://{CORE_HOST}:8000/events/ingest"

print(" [ Intel ] IOC Manager Online")
print(" [ Intel ] Syncing 'Known Bad' IP/Hash List...")

def simulate_sync():
    if random.random() < 0.4: # 40% chance (increased for visibility)
        event = {
            "event_meta": {
                "event_type": "INFO",
                "origin_module": "intel.ioc-manager",
                "severity": "INFO",
                "classification": "SIMULATION"
            },
            "context": {},
            "payload": {
                "action": "SYNC_COMPLETE",
                "new_iocs": random.randint(5, 50),
                "source": "AlienVault OTX"
            }
        }
        try:
            requests.post(CORE_API_URL, json=event, timeout=10)
            print(" [ Intel ] IOC List Synced")
        except Exception as e:
            print(f" [ Intel ] Error: {e}")

while True:
    simulate_sync()
    time.sleep(30)
