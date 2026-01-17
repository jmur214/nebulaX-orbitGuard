import subprocess
import time
import os
import signal
import sys
import sys

# Configuration
SERVICES = [
    {
        "name": "Core API",
        "path": "services/core",
        "cmd": ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
        "env": {},
        "port": 8000
    },
    {
        "name": "Target Web",
        "path": "services/target/public-web",
        "cmd": ["python3", "app.py"],
        "env": {},
        "port": 5000
    },
    {
        "name": "Honeypot",
        "path": "services/blue-team/honeypot-ssh",
        "cmd": ["python3", "main.py"],
        "env": {"CORE_HOST": "localhost"},
        "port": 2222
    },
    {
        "name": "Space Tracker",
        "path": "services/space-guard/tracker",
        "cmd": ["python3", "main.py"],
        "env": {"CORE_HOST": "localhost"},
        "port": None
    },
    {
        "name": "Red Attacker",
        "path": "services/red-team/attack-engine",
        "cmd": ["python3", "main.py"],
        "env": {
            "CORE_HOST": "localhost",
            "WEB_TARGET": "http://localhost:5000",
            "SSH_TARGET": "localhost",
            "SSH_PORT": "2222"
        },
        "port": None
    },
    {
        "name": "Blue Sentinel",
        "path": "services/blue-team/detection-engine",
        "cmd": ["python3", "main.py"],
        "env": {"CORE_HOST": "localhost"},
        "port": None
    },
    # --- ADDED SERVICES ---
    {
        "name": "C2 Beacon",
        "path": "services/red-team/c2-beacon",
        "cmd": ["python3", "main.py"],
        "env": {"CORE_HOST": "localhost"},
        "port": None
    },
    {
        "name": "Vuln Scanner",
        "path": "services/red-team/vuln-scanner",
        "cmd": ["python3", "main.py"],
        "env": {"CORE_HOST": "localhost"},
        "port": None
    },
    {
        "name": "Password Auditor",
        "path": "services/red-team/password-auditor",
        "cmd": ["python3", "main.py"],
        "env": {"CORE_HOST": "localhost"},
        "port": None
    },
    {
        "name": "Ransomware Sim",
        "path": "services/red-team/ransomware-sim",
        "cmd": ["python3", "main.py"],
        "env": {"CORE_HOST": "localhost"},
        "port": None
    },
    {
        "name": "Web Injector",
        "path": "services/red-team/web-injector",
        "cmd": ["python3", "main.py"],
        "env": {"CORE_HOST": "localhost"},
        "port": None
    },
    {
        "name": "APT Emulator",
        "path": "services/red-team/apt-emulator",
        "cmd": ["python3", "main.py"],
        "env": {"CORE_HOST": "localhost"},
        "port": None
    },
    {
        "name": "Net Watchdog",
        "path": "services/blue-team/net-watchdog",
        "cmd": ["python3", "main.py"],
        "env": {"CORE_HOST": "localhost"},
        "port": None
    },
    {
        "name": "Net Forensics",
        "path": "services/blue-team/network-forensics",
        "cmd": ["python3", "main.py"],
        "env": {"CORE_HOST": "localhost"},
        "port": None
    },
    {
        "name": "IDS Suricata",
        "path": "services/blue-team/ids-suricata",
        "cmd": ["python3", "main.py"],
        "env": {"CORE_HOST": "localhost"},
        "port": None
    },
    {
        "name": "EDR Agent",
        "path": "services/blue-team/edr-agent",
        "cmd": ["python3", "main.py"],
        "env": {"CORE_HOST": "localhost"},
        "port": None
    },
    {
        "name": "Policy Mapper",
        "path": "services/grc/policy-mapper",
        "cmd": ["python3", "main.py"],
        "env": {"CORE_HOST": "localhost"},
        "port": None
    },
    {
        "name": "Incident Reporter",
        "path": "services/grc/incident-reporter",
        "cmd": ["python3", "main.py"],
        "env": {"CORE_HOST": "localhost"},
        "port": None
    },
    {
        "name": "CVE Feeder",
        "path": "services/intel/cve-feeder",
        "cmd": ["python3", "main.py"],
        "env": {"CORE_HOST": "localhost"},
        "port": None
    },
    {
        "name": "IOC Manager",
        "path": "services/intel/ioc-manager",
        "cmd": ["python3", "main.py"],
        "env": {"CORE_HOST": "localhost"},
        "port": None
    },
    {
        "name": "RF Receiver",
        "path": "services/space-guard/rf-receiver",
        "cmd": ["python3", "main.py"],
        "env": {"CORE_HOST": "localhost"},
        "port": None
    }
]

processes = []

def is_port_open(port):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def start_service(service):
    print(f"🚀 Starting {service['name']}...")
    
    # If it has a port, check if it's already running
    if service['port'] and is_port_open(service['port']):
        print(f"   ⚠️  Port {service['port']} is already in use. Assuming {service['name']} is running externally.")
        return None

    # Prepare Environment
    env = os.environ.copy()
    env.update(service.get('env', {}))

    # Start Process
    try:
        p = subprocess.Popen(
            service['cmd'],
            cwd=service['path'],
            env=env,
            stdout=subprocess.DEVNULL, # Hide output to keep terminal clean
            stderr=subprocess.PIPE     # Capture errors if needed
        )
        return p
    except Exception as e:
        print(f"   ❌ Failed to start: {e}")
        return None

def cleanup(signum, frame):
    print("\n\n🛑 Shutting down Wargame Simulation...")
    for p in processes:
        if p:
            p.terminate()
    print("✅ All processes terminated.")
    sys.exit(0)

def main():
    print("========================================")
    print("   ASTRA DYNAMICS // WARGAME SIMULATION")
    print("========================================")
    print("Press Ctrl+C to stop the simulation.\n")

    # Register signal handler
    signal.signal(signal.SIGINT, cleanup)

    # Start Services
    for service in SERVICES:
        p = start_service(service)
        if p:
            processes.append(p)
        time.sleep(1) # Stagger start

    print("\n✅ Simulation Active!")
    print("   - Core API: http://localhost:8000")
    print("   - Dashboard: http://localhost:3000 (Run 'npm run dev' separately)")
    print("   - Agents are generating traffic...")

    # Monitor Loop
    while True:
        time.sleep(1)
        # Check if any process died
        for i, p in enumerate(processes):
            if p and p.poll() is not None:
                print(f"⚠️  Process {SERVICES[i]['name']} died unexpectedly.")
                # Optional: Restart logic could go here

if __name__ == "__main__":
    main()
