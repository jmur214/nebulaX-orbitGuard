# NEBULAX SYSTEM CONTEXT & ARCHITECTURAL HANDOFF

## 1. CORE ARCHITECTURAL CONSTRAINTS
**IMPORTANT:** This project operates under a specific set of constraints to ensure stability on the host machine (MacBook Air M1/M2).

* **Hybrid Workflow (Strict):**
    * **Docker** is ONLY used for Infrastructure (`postgres`, `redis`).
    * **Application Logic** (Python/Node) runs **Natively** on the Host.
    * *Reasoning:* To avoid Docker VM disk bloat (`overlay2` storage exhaustion) and compilation errors with C++ dependencies on Alpine Linux.
    * **AI Instruction:** Do NOT write `docker-compose` commands that build images unless explicitly requested for deployment. Assume the user is running scripts via `python main.py` or `npm run dev`.

* **Networking Protocol:**
    * **Internal (Docker-to-Docker):** `http://nebulax-core:8000`
    * **Hybrid (Host-to-Docker):** `http://localhost:8000` (Core API) and `http://localhost:6379` (Redis).
    * **Agent-to-Core:** All Python agents (`red`, `blue`, `space`) must allow configuration of the API URL via the variable `CORE_API_URL` to support both modes.

## 2. FILE SYSTEM TOPOLOGY
The project follows a strict Monorepo structure split by "Team" (Red, Blue, Space).

```text
nebulax-orbitguard/
├── docker-compose.yml          # Infrastructure definition (DB, Redis)
├── services/
│   ├── core/                   # The Brain
│   │   ├── main.py             # FastAPI Gateway & Event Bus
│   │   ├── schemas.py          # Pydantic Models (Universal Event Schema)
│   │   └── db/                 # SQLAlchemy Models (Postgres)
│   │
│   ├── dashboard/              # The Face
│   │   ├── src/pages/index.js  # Main UI (Event Log + Telemetry)
│   │   └── src/components/     # SatelliteMap.js (Leaflet 2D - NO 3D GLOBES)
│   │
│   ├── space-guard/            # The Physics & OT
│   │   ├── tracker/            # Skyfield Propagator (Calculates Look Angles)
│   │   └── ground-sim/         # Vulnerable Ground Station API
│   │
│   ├── red-team/               # The Offense
│   │   ├── attack-engine/      # Hybrid Bot (SSH Brute Force + Web SQLi)
│   │   ├── password-auditor/   # Hash Cracker (Dictionary Attack)
│   │   ├── vuln-scanner/       # Nmap Wrapper (Port Scanning)
│   │   └── c2-beacon/          # Malware Implant (Heartbeat Simulation)
│   │
│   ├── blue-team/              # The Defense
│   │   ├── honeypot-ssh/       # High-Interaction Trap (Paramiko)
│   │   └── detection-engine/   # SIEM Sentinel (Log Analysis)
│   │
│   └── target/                 # The Battlefield
│       └── public-web/         # "Astra Dynamics" Portal (Vulnerable Flask App)

3. THE UNIVERSAL EVENT SCHEMA (The API Contract)
All modules communicate via a single JSON structure. Any new module MUST adhere to this format or the Core will reject it (HTTP 422).

JSON Structure:
{
  "event_meta": {
    "origin_module": "string (e.g., 'red.c2.beacon')",
    "event_type": "ENUM (See Registry Below)",
    "severity": "INFO | LOW | MEDIUM | HIGH | CRITICAL",
    "classification": "SIMULATION"
  },
  "context": {
    "related_ip": "IP Address",
    "related_asset_id": "Asset Name",
    "mitre_attack_id": "T-Code (Optional)"
  },
  "payload": {
    "key": "value" // Dynamic dict based on event type
  }
}
Event Type Registry (As defined in services/core/schemas.py):

TLE_UPDATE: Satellite telemetry (Az/El/Lat/Lon).

AUTH_FAILURE: Failed login attempt (Honeypot/Web).

EXPLOIT_SUCCESS: Successful Red Team breach.

CREDENTIAL_CRACKED: Red Team successfully cracked a captured hash.

VULN_REPORT: Scanner found an open port.

WEB_TRAFFIC: Normal/Abnormal web access logs.

NETWORK_FLOW: C2 Beacon traffic metadata.

COMMAND_EXECUTED: Attacker typed a command in the Honeypot.

THREAT_DETECTED: Blue Team SIEM logic triggered an alert.

4. MODULE-SPECIFIC INTELLIGENCE
Space Tracker: Uses skyfield. Must calculate BOTH Barycentric coordinates (for Look Angles) and Geocentric coordinates (for Map Lat/Lon) separately to avoid coordinate frame errors.

Dashboard: Uses leaflet and react-leaflet. Do not attempt to use react-globe.gl or three.js—these libraries cause node-gyp compilation failures on the host environment. Stick to 2D maps.

Honeypot: Uses paramiko. Requires a generated server.key file to start. It mimics an Ubuntu server and logs keystrokes to the Core.

Target Web: Uses flask with check_same_thread=False for SQLite to allow concurrent simulated attacks. Contains intentional SQL Injection at the /login endpoint.

5. DEVELOPMENT PROTOCOL
For new modules:

Pattern Match: Always copy the requirements.txt / Dockerfile pattern from existing modules (Python 3.10-slim).

Logging: Every module must have a log_event() function that POSTs to the Core API.

Config: All API URLs must be configurable via environment variables or top-level constants to switch between localhost (Hybrid) and nebulax-core (Docker).

