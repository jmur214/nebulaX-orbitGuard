import time
import requests
import schedule

# CONFIGURATION
# Use host gateway to talk to Core
CORE_READ_URL = "http://host.docker.internal:8000/events/recent"
CORE_WRITE_URL = "http://host.docker.internal:8000/events/ingest"

# Load Wordlist
print(" [ Red Team ] Loading Breach Database (rockyou_sample.txt)...")
try:
    with open("rockyou_sample.txt", "r") as f:
        WEAK_PASSWORDS = set(line.strip() for line in f)
    print(f" [ Red Team ] Database Loaded: {len(WEAK_PASSWORDS)} hashes.")
except Exception as e:
    print(f" [!] Error loading wordlist: {e}")
    WEAK_PASSWORDS = set()

# Memory to avoid re-processing the same event
processed_ids = set()

def report_crack(username, password, source_ip):
    print(f" [!!!] CRACKED: {username}:{password}")
    
    event = {
        "event_meta": {
            "origin_module": "red.password.auditor",
            "event_type": "CREDENTIAL_CRACKED",
            "severity": "HIGH",
            "classification": "SIMULATION"
        },
        "context": {
            "related_ip": source_ip,
            "mitre_attack_id": "T1110.004 (Credential Stuffing)"
        },
        "payload": {
            "cracked_user": username,
            "weak_password": password,
            "method": "Dictionary Attack"
        }
    }
    try:
        requests.post(CORE_WRITE_URL, json=event)
    except:
        pass

def run_audit_cycle():
    global processed_ids
    
    try:
        # 1. Get recent events from the Core
        resp = requests.get(f"{CORE_READ_URL}?limit=50")
        if resp.status_code != 200: 
            return

        events = resp.json()
        
        for event in events:
            ev_id = event.get('id')
            ev_type = event.get('event_type')
            
            if not ev_id or ev_id in processed_ids:
                continue
            
            processed_ids.add(ev_id)

            # We are looking for AUTH_FAILURE events from Honeypots or Web
            if ev_type == "AUTH_FAILURE":
                payload = event.get('payload', {})
                context = event.get('context', {})
                
                # Extract credentials trapped by the sensor
                captured_pass = payload.get('password')
                captured_user = payload.get('username')
                source_ip = context.get('related_ip') if context else 'unknown'

                if captured_pass and captured_pass in WEAK_PASSWORDS:
                    print(f" [+] Weak Credential Identified: {captured_user} using '{captured_pass}'")
                    report_crack(captured_user, captured_pass, source_ip)

    except Exception as e:
        print(f" [!] Cycle Error: {e}")
    
    # Cleanup memory
    if len(processed_ids) > 1000:
        processed_ids.clear()

# Run often (real-time interception)
print(" [ Red Team ] Password Auditor Online. Sniffing bus...")
schedule.every(5).seconds.do(run_audit_cycle)

while True:
    schedule.run_pending()
    time.sleep(1)