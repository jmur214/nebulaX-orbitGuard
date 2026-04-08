import time
import os
import random
import requests
import json
from datetime import datetime
from faker import Faker

fake = Faker()

# CONFIGURATION
CORE_HOST = os.getenv("CORE_HOST", "nebulax-core")
CORE_API_URL = f"http://{CORE_HOST}:8000/events/ingest"

print(" [ Target ] Identity Manager Online")
print(" [ Target ] Generating synthetic employee personas...")

def simulate_activity():
    if random.random() < 0.5: # 50% chance (increased for visibility)
        profile = fake.profile()
        event = {
            "event_meta": {
                "event_type": "AUTH_FAILURE",
                "origin_module": "target.identity-manager",
                "severity": "LOW",
                "classification": "SIMULATION"
            },
            "context": {},
            "payload": {
                "username": profile['username'],
                "email": profile['mail'],
                "reason": "BAD_PASSWORD"
            }
        }
        try:
            requests.post(CORE_API_URL, json=event, timeout=2)
            print(f" [ Identity ] Auth Failure: {profile['username']}")
        except Exception as e:
            print(f" [ Identity ] Error: {e}")

while True:
    simulate_activity()
    time.sleep(20)
