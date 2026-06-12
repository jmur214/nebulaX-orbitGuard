import time
import os
import random
import requests

# CONFIGURATION
CORE_HOST = os.getenv("CORE_HOST", "nebulax-core")
CORE_API_URL = f"http://{CORE_HOST}:8000/events/ingest"

print(" [ Target ] Internal Infrastructure Simulation Online")
print(" [ Target ] Simulating SMB Shares and Active Directory...")

def simulate_activity():
    if random.random() < 0.6: # 60% chance (increased for visibility)
        event = {
            "event_meta": {
                "event_type": "NETWORK_FLOW",
                "origin_module": "target.internal-infra",
                "severity": "INFO",
                "classification": "SIMULATION"
            },
            "context": {},
            "payload": {
                "protocol": "SMB",
                "source_ip": "192.168.1.10",
                "dest_ip": "192.168.1.5",
                "action": "FILE_ACCESS"
            }
        }
        try:
            requests.post(CORE_API_URL, json=event, timeout=2)
            print(" [ Internal ] SMB Traffic Simulated")
        except Exception as e:
            print(f" [ Internal ] Error: {e}")

while True:
    simulate_activity()
    time.sleep(15)
