import time
import os
import random
import requests

# CONFIGURATION
CORE_HOST = os.getenv("CORE_HOST", "nebulax-core")
CORE_API_URL = f"http://{CORE_HOST}:8000/events/ingest"
TARGET_URL = "http://nebulax-target-web:5000"

print(" [ Red Team ] Web Injector Online")
print(" [ Red Team ] Loading Payloads (SQLi, XSS)...")

PAYLOADS = [
    "' OR 1=1 --",
    "<script>alert(1)</script>",
    "admin' --",
    "../../../../etc/passwd"
]

def simulate_attack():
    if random.random() < 0.5: # 50% chance (increased for visibility)
        payload = random.choice(PAYLOADS)
        # 1. Simulate the actual attack (fire and forget)
        try:
            # In a real scenario, this would hit the target. 
            # For now, we just log the "attempt" as an event.
            pass 
        except:
            pass
        
        # 2. Log the event to Core
        event = {
            "event_meta": {
                "event_type": "WEB_TRAFFIC",
                "origin_module": "red.web-injector",
                "severity": "HIGH",
                "classification": "SIMULATION"
            },
            "context": {},
            "payload": {
                "method": "POST",
                "url": "/login",
                "payload": payload,
                "status": 403
            }
        }
        try:
            requests.post(CORE_API_URL, json=event, timeout=2)
            print(f" [ Injector ] Fired: {payload}")
        except Exception as e:
            print(f" [ Injector ] Error: {e}")

while True:
    simulate_attack()
    time.sleep(15)
