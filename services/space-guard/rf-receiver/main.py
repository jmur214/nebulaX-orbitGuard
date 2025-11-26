import time
import os
import random
import requests
import json
from datetime import datetime

# CONFIGURATION
CORE_HOST = os.getenv("CORE_HOST", "nebulax-core")
CORE_API_URL = f"http://{CORE_HOST}:8000/events/ingest"

print(" [ Space ] RF Receiver Online")
print(" [ Space ] Initializing RTL-SDR Interface...")

def simulate_rf():
    if random.random() < 0.3:
        freq = f"{random.randint(400, 450)}.00 MHz"
        event = {
            "event_meta": {
                "event_type": "RF_SIGNAL_CAPTURED",
                "origin_module": "space.rf-receiver",
                "severity": "INFO",
                "classification": "SIMULATION"
            },
            "context": {},
            "payload": {
                "frequency": freq,
                "strength": f"-{random.randint(30, 90)} dBm",
                "modulation": "FM"
            }
        }
        try:
            requests.post(CORE_API_URL, json=event, timeout=2)
            print(f" [ Space ] Signal Captured: {freq}")
        except Exception as e:
            print(f" [ Space ] Error: {e}")

while True:
    simulate_rf()
    time.sleep(10)
