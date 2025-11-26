import socket
import threading
import paramiko
import requests
import time
import json
from datetime import datetime

import os

# CONFIGURATION
# We connect to the Core via the host gateway
CORE_HOST = os.getenv("CORE_HOST", "nebulax-core")
CORE_API_URL = f"http://{CORE_HOST}:8000/events/ingest"
HOST_KEY_PATH = 'server.key'
SSH_PORT = 2222 # Internal port

# The "Fake" Filesystem
FAKE_FILES = {
    "ls": "confidential_project_x.pdf  passwords.txt  salary_data.csv",
    "pwd": "/home/admin",
    "whoami": "admin"
}

def log_event(event_type, severity, payload, related_ip):
    """
    Send intelligence to NebulaX Core
    """
    event = {
        "event_meta": {
            "origin_module": "blue.honeypot.ssh",
            "event_type": event_type,
            "severity": severity,
            "classification": "SIMULATION"
        },
        "context": {
            "related_ip": related_ip,
            "related_asset_id": "ASTRA-INTERNAL-SRV-01",
            "mitre_attack_id": "T1078" # Valid Accounts
        },
        "payload": payload
    }
    try:
        requests.post(CORE_API_URL, json=event, timeout=2)
    except Exception as e:
        print(f" [!] Failed to log to Core: {e}")

class HoneyServer(paramiko.ServerInterface):
    def __init__(self, client_ip):
        self.client_ip = client_ip
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        # LOG THE ATTEMPT
        print(f" [*] Auth Attempt: {username}:{password} from {self.client_ip}")
        
        log_event(
            "AUTH_FAILURE", # We log it as failure first for visibility
            "LOW",
            {"username": username, "password": password, "status": "ATTEMPT"},
            self.client_ip
        )

        # We accept EVERYTHING to trap them
        # In a real simulation, you might only accept specific weak passwords
        return paramiko.AUTH_SUCCESSFUL

    def get_allowed_auths(self, username):
        return 'password'

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

def handle_connection(client, addr):
    ip = addr[0]
    print(f" [+] New Connection: {ip}")
    
    try:
        transport = paramiko.Transport(client)
        transport.add_server_key(paramiko.RSAKey(filename=HOST_KEY_PATH))
        
        server = HoneyServer(ip)
        try:
            transport.start_server(server=server)
        except paramiko.SSHException:
            return

        # Wait for auth
        chan = transport.accept(20)
        if not chan:
            return

        server.event.wait(10)
        if not server.event.is_set():
            return

        # --- INTERACTIVE SHELL SIMULATION ---
        log_event("AUTH_SUCCESS", "CRITICAL", {"msg": "Attacker gained shell access"}, ip)
        
        chan.send("Welcome to Ubuntu 22.04.2 LTS (GNU/Linux 5.15.0-60-generic x86_64)\r\n")
        chan.send("ASTRA DYNAMICS AUTHORIZED PERSONNEL ONLY\r\n\r\n")
        
        while True:
            chan.send("admin@astra-server:~$ ")
            command = ""
            while not command.endswith("\r"):
                transport = chan.recv(1024)
                chan.send(transport) # Echo back chars
                command += transport.decode("utf-8")
            
            chan.send("\r\n")
            cmd = command.strip()
            
            if cmd == 'exit':
                break
            
            # Log the command
            if cmd:
                print(f" [>] Command executed: {cmd}")
                log_event("COMMAND_EXECUTED", "HIGH", {"command": cmd}, ip)

            # Fake Response
            if cmd in FAKE_FILES:
                chan.send(FAKE_FILES[cmd] + "\r\n")
            elif cmd == "":
                pass
            else:
                chan.send(f"bash: {cmd}: command not found\r\n")

        chan.close()

    except Exception as e:
        print(f" [!] Connection Error: {e}")

# Start Socket Listener
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('0.0.0.0', SSH_PORT))
sock.listen(100)

print(f" [ Astra Honeypot ] Listening on port {SSH_PORT}...")

while True:
    try:
        client, addr = sock.accept()
        threading.Thread(target=handle_connection, args=(client, addr)).start()
    except Exception as e:
        print(f" [!] Accept Error: {e}")