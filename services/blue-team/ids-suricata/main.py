import time
import os
import random
import requests

# CONFIGURATION
CORE_HOST = os.getenv("CORE_HOST", "nebulax-core")
CORE_API_URL = f"http://{CORE_HOST}:8000/events/ingest"

print(" [ Blue Team ] Suricata IDS Online")
print(" [ Blue Team ] Loading ET Open Ruleset...")

ALERTS = [
    "ET MALWARE Cobalt Strike Beacon Observed",
    "ET EXPLOIT Apache Log4j RCE Attempt",
    "ET SCAN Nmap Scripting Engine User-Agent",
    "ET POLICY SSH Root Login Attempt",
    "ET INFO Suspicious User-Agent (Python-requests)"
]

def check_traffic():
    if random.random() < 0.5: # 50% chance of alert (increased for visibility)
        alert = random.choice(ALERTS)
        event = {
            "event_meta": {
                "event_type": "THREAT_DETECTED",
                "origin_module": "blue.ids.suricata",
                "severity": "HIGH" if "Cobalt" in alert or "Log4j" in alert else "MEDIUM",
                "classification": "SIMULATION"
            },
            "context": {},
            "payload": {
                "alert_title": alert,
                "interface": "eth0",
                "protocol": "TCP"
            }
        }
        try:
            requests.post(CORE_API_URL, json=event, timeout=2)
            print(f" [ IDS ] Alert Sent: {alert}")
        except Exception as e:
            print(f" [ IDS ] Error sending alert: {e}")

while True:
    check_traffic()
    time.sleep(10)
