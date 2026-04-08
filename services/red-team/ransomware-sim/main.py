import time
import requests
import schedule
import random
import json
import os

# CONFIGURATION
CORE_HOST = os.getenv("CORE_HOST", "nebulax-core")
CORE_API_URL = f"http://{CORE_HOST}:8000/events/ingest"

# Targets (Internal Docker DNS names or simulated IPs)
TARGETS = ["10.0.0.55 (HR-Workstation)", "10.0.0.12 (CEO-Laptop)", "10.0.0.88 (Finance-Server)"]

FILE_EXTENSIONS = [".docx", ".xlsx", ".pdf", ".jpg", ".sql"]

def encrypt_files():
    target = random.choice(TARGETS)
    file_count = random.randint(5, 50)
    
    print(f" [*] RANSOMWARE: Encrypting {file_count} files on {target}...")
    
    # 1. Send Encryption Event
    event = {
        "event_meta": {
            "origin_module": "red.ransomware",
            "event_type": "FILE_ENCRYPTED",
            "severity": "CRITICAL",
            "classification": "SIMULATION"
        },
        "context": {
            "related_asset_id": target,
            "mitre_attack_id": "T1486 (Data Encrypted for Impact)"
        },
        "payload": {
            "file_count": file_count,
            "algorithm": "AES-256",
            "extensions_affected": random.sample(FILE_EXTENSIONS, 2)
        }
    }
    
    try:
        requests.post(CORE_API_URL, json=event, timeout=2)
    except:
        pass
        
    # 2. Drop Ransom Note (Simulated)
    time.sleep(1)
    note_event = {
        "event_meta": {
            "origin_module": "red.ransomware",
            "event_type": "RANSOM_NOTE",
            "severity": "HIGH",
            "classification": "SIMULATION"
        },
        "context": {
            "related_asset_id": target,
            "mitre_attack_id": "T1491 (Defacement)"
        },
        "payload": {
            "message": "YOUR FILES ARE ENCRYPTED. PAY 5 BTC TO UNLOCK.",
            "wallet_address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        }
    }
    
    try:
        requests.post(CORE_API_URL, json=note_event, timeout=2)
    except:
        pass

# Run randomly between 30 and 90 seconds
def schedule_next_attack():
    delay = random.randint(30, 90)
    schedule.every(delay).seconds.do(encrypt_files).tag('attack')

print(" [ APT Simulation ] Ransomware Module Loaded. Waiting for trigger...")
encrypt_files() # Initial hit

while True:
    schedule.run_pending()
    
    # Reschedule for randomness
    schedule.clear('attack')
    delay = random.randint(20, 60)
    schedule.every(delay).seconds.do(encrypt_files).tag('attack')
    
    time.sleep(1)
