import time
import requests
import schedule
import json

# CONFIGURATION
INTERNAL_URL = "http://nebulax-core:8000"
HOST_URL = "http://host.docker.internal:8000"

processed_alert_ids = set()

print(" [ Blue Forensics ] Resolving Core API connection...")
BASE_URL = ""
try:
    requests.get(f"{INTERNAL_URL}/", timeout=2)
    BASE_URL = INTERNAL_URL
    print(" [ Blue Forensics ] Connected via Internal Docker Network")
except:
    print(" [ Blue Forensics ] Internal DNS failed. Switching to Host Gateway...")
    BASE_URL = HOST_URL

def create_case_file(alert_event, related_ip):
    print(f" [!!!] OPENING CASE FILE FOR: {related_ip}")
    
    # In a real system, we would query all past events for this IP
    # Here we simulate an investigation finding
    
    investigation_summary = f"Investigation into {related_ip} reveals suspicious patterns matching APT behavior."
    
    event = {
        "event_meta": {
            "origin_module": "blue.network.forensics",
            "event_type": "FORENSIC_CASE",
            "severity": "INFO",
            "classification": "SIMULATION"
        },
        "context": {
            "related_ip": related_ip,
            "related_case_id": f"CASE-{int(time.time())}",
            "mitre_attack_id": "T1098 (Account Manipulation)" # Placeholder
        },
        "payload": {
            "case_status": "OPEN",
            "trigger_event": alert_event.get('payload', {}).get('alert_title'),
            "analyst_notes": investigation_summary,
            "evidence_count": 1
        }
    }
    
    try:
        requests.post(f"{BASE_URL}/events/ingest", json=event)
        print(" [***] Case File Submitted to Core.")
    except Exception as e:
        print(f" [!] Failed to submit case: {e}")

def run_forensics_cycle():
    global processed_alert_ids
    print(" [?] Checking for new alerts...", end="\r")
    
    try:
        # Look for THREAT_DETECTED events from Sentinel or Watchdog
        resp = requests.get(f"{BASE_URL}/events/recent?limit=20", timeout=2)
        if resp.status_code != 200:
            return
        
        events = resp.json()
        
        for event in events:
            ev_id = event.get('id')
            ev_type = event.get('event_type')
            
            if ev_type != 'THREAT_DETECTED':
                continue
                
            if ev_id in processed_alert_ids:
                continue
            
            print(f"\n [!] ANALYZING ALERT: {ev_id}")
            processed_alert_ids.add(ev_id)
            
            context = event.get('context', {})
            ip = context.get('related_ip')
            
            if ip and ip != 'unknown':
                create_case_file(event, ip)

    except Exception as e:
        print(f"\n [!] Forensics Cycle Error: {e}")

print(" [ Blue Forensics ] Automated Investigator Online.")
schedule.every(10).seconds.do(run_forensics_cycle)

while True:
    schedule.run_pending()
    time.sleep(1)
