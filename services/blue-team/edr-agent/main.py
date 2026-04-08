import time
import os
import random
import requests
import json
from datetime import datetime

# CONFIGURATION
CORE_HOST = os.getenv("CORE_HOST", "nebulax-core")
CORE_API_URL = f"http://{CORE_HOST}:8000/events/ingest"

print(" [ Blue Team ] EDR Agent Online")
print(" [ Blue Team ] Hooking Kernel Syscalls...")

ALERTS = [
    "Suspicious Process Creation (powershell.exe -enc)",
    "LSASS Memory Dump Attempt",
    "Unsigned Driver Load",
    "Registry Key Persistence Added"
]

def simulate_activity():
    if random.random() < 0.5: # 50% chance (increased for visibility)
        alert = random.choice(ALERTS)
        event = {
            "event_meta": {
                "event_type": "THREAT_DETECTED",
                "origin_module": "blue.edr-agent",
                "severity": "HIGH",
                "classification": "SIMULATION"
            },
            "context": {},
            "payload": {
                "alert": alert,
                "process_id": random.randint(1000, 9999),
                "user": "SYSTEM"
            }
        }
        try:
            requests.post(CORE_API_URL, json=event, timeout=2)
            print(f" [ EDR ] Alert: {alert}")
        except Exception as e:
            print(f" [ EDR ] Error: {e}")

while True:
    simulate_activity()
    time.sleep(15)
