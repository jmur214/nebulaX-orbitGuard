import time
import os
import random
import requests

# CONFIGURATION
CORE_HOST = os.getenv("CORE_HOST", "nebulax-core")
CORE_API_URL = f"http://{CORE_HOST}:8000/events/ingest"

print(" [ Red Team ] APT Emulator Online")
print(" [ Red Team ] Initializing Kill Chain Simulation...")

STAGES = [
    "Reconnaissance",
    "Weaponization",
    "Delivery",
    "Exploitation",
    "Installation",
    "C2",
    "Actions on Objectives"
]

def simulate_campaign():
    if random.random() < 0.5: # 50% chance (increased for visibility)
        stage = random.choice(STAGES)
        event = {
            "event_meta": {
                "event_type": "COMMAND_EXECUTED",
                "origin_module": "red.apt-emulator",
                "severity": "CRITICAL",
                "classification": "SIMULATION"
            },
            "context": {
                "mitre_attack_id": "T1059"
            },
            "payload": {
                "stage": stage,
                "command": "whoami /all",
                "user": "nt authority\\system"
            }
        }
        try:
            requests.post(CORE_API_URL, json=event, timeout=2)
            print(f" [ APT ] Campaign Stage: {stage}")
        except Exception as e:
            print(f" [ APT ] Error: {e}")

while True:
    simulate_campaign()
    time.sleep(20)
