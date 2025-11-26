import time
import requests
import schedule
from datetime import datetime

# CONFIGURATION
INTERNAL_URL = "http://nebulax-core:8000"
HOST_URL = "http://host.docker.internal:8000"

# Memory to prevent spamming alerts for the same event ID
processed_event_ids = set()

def get_api_url(endpoint):
    try:
        requests.get(f"{INTERNAL_URL}/", timeout=1)
        return f"{INTERNAL_URL}{endpoint}"
    except:
        return f"{HOST_URL}{endpoint}"

print(" [ Blue Team ] Resolving Core API connection...")
BASE_URL = ""
try:
    requests.get(f"{INTERNAL_URL}/", timeout=2)
    BASE_URL = INTERNAL_URL
    print(" [ Blue Team ] Connected via Internal Docker Network")
except:
    print(" [ Blue Team ] Internal DNS failed. Switching to Host Gateway...")
    BASE_URL = HOST_URL

print(f" [ Blue Team ] Target Core: {BASE_URL}")

def trigger_alert(severity, title, description, related_ip):
    print(f" [!!!] TRIGGERING ALERT: {title}")
    
    event = {
        "event_meta": {
            "origin_module": "blue.sentinel",
            "event_type": "THREAT_DETECTED",
            "severity": severity,
            "classification": "SIMULATION"
        },
        "context": {
            "related_ip": related_ip,
            "mitre_attack_id": "T1078"
        },
        "payload": {
            "alert_title": title,
            "description": description,
            "action_taken": "IP_BLOCKED"
        }
    }
    try:
        r = requests.post(f"{BASE_URL}/events/ingest", json=event)
        print(f" [!!!] Alert Sent Status: {r.status_code}")
    except Exception as e:
        print(f" [!] Failed to send alert: {e}")

def run_detection_cycle():
    global processed_event_ids
    print(" [?] Polling for threats...", end="\r")
    
    try:
        resp = requests.get(f"{BASE_URL}/events/recent?limit=20", timeout=2)
        if resp.status_code != 200:
            print(f" [!] API Error: {resp.status_code}")
            return
        
        events = resp.json()
        
        for event in events:
            # --- FIX IS HERE ---
            # The Read API returns a flat structure, not nested event_meta
            # We use .get() to be safe
            ev_id = event.get('id')
            ev_type = event.get('event_type')
            
            if not ev_id or not ev_type:
                continue
            
            # Skip if already analyzed
            if ev_id in processed_event_ids:
                continue
            
            # RULE: Detect Successful Exploits
            if ev_type == 'EXPLOIT_SUCCESS':
                print(f"\n [XXX] NEW THREAT FOUND: {ev_id} | Type: {ev_type}")
                
                processed_event_ids.add(ev_id)
                
                # Extract IP from context (which IS nested)
                context = event.get('context', {})
                ip = context.get('related_ip', 'unknown') if context else 'unknown'

                trigger_alert(
                    "CRITICAL",
                    "Active Intrusion Detected",
                    "Red Team engine reported successful breach.",
                    ip
                )

    except Exception as e:
        print(f"\n [!] Detection Cycle Error: {e}")

print(" [ Blue Team ] Sentinel Engine Online. Hunting...")
schedule.every(2).seconds.do(run_detection_cycle)

while True:
    schedule.run_pending()
    time.sleep(1)