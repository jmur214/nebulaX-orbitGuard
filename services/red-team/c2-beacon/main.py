import time
import requests
import schedule
import random
import json
import numpy as np # For realistic jitter distribution

# CONFIGURATION
CORE_API_URL = "http://core-api:8000/events/ingest"

# Simulated C2 Infrastructure (The "Bad Guys")
C2_SERVERS = [
    {"ip": "185.100.84.21", "country": "RU", "threat_group": "APT29"},
    {"ip": "45.122.99.12", "country": "CN", "threat_group": "APT41"},
    {"ip": "103.15.66.88", "country": "KP", "threat_group": "Lazarus"}
]

# Simulated Infected Hosts (Internal)
INFECTED_HOSTS = ["10.0.0.55 (HR-Workstation)", "10.0.0.12 (CEO-Laptop)"]

def send_beacon():
    """
    Simulates a 'Heartbeat' or 'Data Exfiltration' packet.
    """
    c2 = random.choice(C2_SERVERS)
    victim = random.choice(INFECTED_HOSTS)
    
    # Simulate Data Size (Small heartbeat vs Large exfiltration)
    is_exfil = random.random() > 0.9 # 10% chance of data theft
    packet_size = random.randint(50000, 5000000) if is_exfil else random.randint(200, 500)
    
    print(f" [*] BEACON: {victim} -> {c2['ip']} ({packet_size} bytes)")

    # We log this as 'NETWORK_FLOW' so the Blue Team can analyze it later
    event = {
        "event_meta": {
            "origin_module": "red.c2.beacon",
            "event_type": "NETWORK_FLOW", # New Event Type
            "severity": "INFO", # Network traffic is neutral until analyzed
            "classification": "SIMULATION"
        },
        "context": {
            "related_ip": c2['ip'], # The external bad IP
            "related_asset_id": victim,
            "mitre_attack_id": "T1071 (Application Layer Protocol)"
        },
        "payload": {
            "destination_country": c2['country'],
            "bytes_out": packet_size,
            "protocol": "HTTPS",
            "threat_signature": c2['threat_group'] # For easy debugging
        }
    }
    
    try:
        response = requests.post(CORE_API_URL, json=event)
        print(f" [>] Response: {response.status_code} - {response.text}")
    except Exception as e:
        print(f" [!] ERROR sending beacon: {e}")

# JITTER LOGIC
# Real malware sleeps for random intervals to hide.
# We use a random schedule instead of a fixed 5 seconds.
def schedule_next_beacon():
    # Sleep between 5 and 15 seconds (Gaussian distribution would be better, but random is fine)
    delay = random.randint(5, 15)
    schedule.every(delay).seconds.do(send_beacon).tag('beacon')

# Start the loop
print(" [ APT Simulation ] C2 Beacon Active. Initializing implants...")
send_beacon()

while True:
    schedule.run_pending()
    
    # Clear old job and schedule new one (Variable Interval)
    schedule.clear('beacon')
    delay = random.randint(10, 30) 
    schedule.every(delay).seconds.do(send_beacon).tag('beacon')
    
    time.sleep(1)