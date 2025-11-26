import time
import requests
import schedule
import json

# CONFIGURATION
INTERNAL_URL = "http://nebulax-core:8000"
HOST_URL = "http://host.docker.internal:8000"

# Memory to prevent spamming alerts
processed_event_ids = set()

print(" [ Blue Watchdog ] Resolving Core API connection...")
BASE_URL = ""
try:
    requests.get(f"{INTERNAL_URL}/", timeout=2)
    BASE_URL = INTERNAL_URL
    print(" [ Blue Watchdog ] Connected via Internal Docker Network")
except:
    print(" [ Blue Watchdog ] Internal DNS failed. Switching to Host Gateway...")
    BASE_URL = HOST_URL

print(f" [ Blue Watchdog ] Target Core: {BASE_URL}")

def trigger_alert(severity, title, description, related_ip, context_data=None):
    print(f" [!!!] WATCHDOG ALERT: {title}")
    
    event = {
        "event_meta": {
            "origin_module": "blue.net.watchdog",
            "event_type": "THREAT_DETECTED",
            "severity": severity,
            "classification": "SIMULATION"
        },
        "context": {
            "related_ip": related_ip,
            "mitre_attack_id": "T1048 (Exfiltration)" if "Exfiltration" in title else "T1046 (Network Service Discovery)"
        },
        "payload": {
            "alert_title": title,
            "description": description,
            "action_taken": "TRAFFIC_LOGGED",
            "additional_data": context_data or {}
        }
    }
    try:
        requests.post(f"{BASE_URL}/events/ingest", json=event)
    except Exception as e:
        print(f" [!] Failed to send alert: {e}")

def run_watchdog_cycle():
    global processed_event_ids
    print(" [?] Scanning network flows...", end="\r")
    
    try:
        # Fetch recent events
        resp = requests.get(f"{BASE_URL}/events/recent?limit=50", timeout=2)
        if resp.status_code != 200:
            return
        
        events = resp.json()
        
        for event in events:
            ev_id = event.get('id')
            ev_type = event.get('event_type')
            
            if not ev_id or not ev_type:
                continue
            
            if ev_id in processed_event_ids:
                continue
            
            # RULE 1: Detect Large Data Exfiltration (C2)
            if ev_type == 'NETWORK_FLOW':
                payload = event.get('payload', {})
                bytes_out = payload.get('bytes_out', 0)
                
                # Threshold: 1MB (1,000,000 bytes)
                if bytes_out > 1000000:
                    print(f"\n [XXX] EXFILTRATION DETECTED: {bytes_out} bytes")
                    processed_event_ids.add(ev_id)
                    
                    context = event.get('context', {})
                    ip = context.get('related_ip', 'unknown')
                    
                    trigger_alert(
                        "HIGH",
                        "Data Exfiltration Detected",
                        f"Large outbound traffic flow detected: {bytes_out} bytes to {ip}",
                        ip,
                        {"flow_id": ev_id}
                    )

            # RULE 2: Detect Critical Vulnerabilities
            elif ev_type == 'VULN_REPORT':
                # We want to alert if the Red Team finds something
                processed_event_ids.add(ev_id)
                
                payload = event.get('payload', {})
                port = payload.get('port')
                service = payload.get('service')
                
                context = event.get('context', {})
                target = context.get('related_asset_id', 'unknown')
                
                print(f"\n [XXX] VULNERABILITY FLAGGED: {target}:{port}")
                
                trigger_alert(
                    "MEDIUM",
                    "Open Vulnerable Port Detected",
                    f"Scanner found open port {port} ({service}) on {target}",
                    target,
                    {"vuln_id": ev_id}
                )

    except Exception as e:
        print(f"\n [!] Watchdog Cycle Error: {e}")

print(" [ Blue Watchdog ] Network Monitor Online.")
schedule.every(5).seconds.do(run_watchdog_cycle)

while True:
    schedule.run_pending()
    time.sleep(1)
