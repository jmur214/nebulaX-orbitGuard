import nmap
import requests
import schedule
import time

import os

# CONFIGURATION
CORE_HOST = os.getenv("CORE_HOST", "nebulax-core")
CORE_API_URL = f"http://{CORE_HOST}:8000/events/ingest"

# Targets to scan (Internal Docker DNS names)
TARGETS = ["nebulax-target-web", "nebulax-honeypot"]

def report_vuln(target, port, state, service):
    print(f" [!] VULNERABILITY FOUND: {target}:{port} ({service}) is {state}")
    
    event = {
        "event_meta": {
            "origin_module": "red.vuln.scanner",
            "event_type": "VULN_REPORT",
            "severity": "MEDIUM",
            "classification": "SIMULATION"
        },
        "context": {
            "related_asset_id": target,
            "mitre_attack_id": "T1046 (Network Service Discovery)"
        },
        "payload": {
            "port": port,
            "state": state,
            "service": service,
            "recommendation": "Close port if not required or implement firewall rules."
        }
    }
    try:
        requests.post(CORE_API_URL, json=event)
    except Exception as e:
        print(f"Failed to report: {e}")

def run_scan_cycle():
    nm = nmap.PortScanner()
    print(" [ Scanner ] Starting Network Reconnaissance...")
    
    for target in TARGETS:
        try:
            # Resolve the IP of the container name
            print(f" [*] Scanning Target: {target}")
            # Scan common ports
            nm.scan(hosts=target, arguments='-p 22,80,443,5000,8080,2222 -sV')
            
            # Iterate through results
            for host in nm.all_hosts():
                for proto in nm[host].all_protocols():
                    lport = nm[host][proto].keys()
                    for port in lport:
                        state = nm[host][proto][port]['state']
                        service = nm[host][proto][port]['name']
                        
                        if state == 'open':
                            report_vuln(target, port, state, service)
                            
        except Exception as e:
            print(f" [!] Scan Error for {target}: {e}")

# Run scan every 60 seconds (Recon is slow)
schedule.every(60).seconds.do(run_scan_cycle)

# Initial run
run_scan_cycle()

while True:
    schedule.run_pending()
    time.sleep(1)