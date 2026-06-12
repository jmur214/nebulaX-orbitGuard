# NebulaX System Context & Architecture

## 1. Architectural Pattern: Event-Driven Microservices
**Why?** To simulate a real-world enterprise environment where disparate systems (Space, IT, OT) must communicate without tight coupling.

*   **The Nervous System (Event Bus):**
    *   **Technology:** Redis Pub/Sub.
    *   **Function:** Decouples producers (Sensors/Attackers) from consumers (Dashboard/SIEM).
    *   **Flow:** `Module` -> `Core API (Ingest)` -> `Redis` -> `Core API (Stream)` -> `Dashboard`.

*   **The Brain (Core API):**
    *   **Technology:** FastAPI (Python).
    *   **Role:** Enforces the `UniversalEvent` schema. Rejects malformed data (HTTP 422).
    *   **Storage:** PostgreSQL (JSONB) for long-term retention and "Replay" capability.

## 2. Universal Event Schema
**Critical Constraint:** All modules MUST speak the same language.

```json
{
  "event_meta": {
    "origin_module": "space.tracker",
    "event_type": "TLE_UPDATE",
    "severity": "INFO",
    "classification": "UNCLASSIFIED"
  },
  "context": {
    "timestamp": "ISO8601",
    "related_asset_id": "SAT-25544"
  },
  "payload": {
    "arbitrary_data": "..."
  }
}
```

## 3. System Topology (Detailed)
The system is organized into functional "Pillars" within the `services/` directory.

```text
services/
├── core/                   # [Port 8000] The API Gateway & Event Bus
├── dashboard/              # [Port 3000] The Next.js Frontend
├── space-guard/            # Orbital Mechanics & RF
│   ├── tracker/            # TLE Propagation (Skyfield)
│   ├── ground-sim/         # Rotator Control Simulation
│   └── rf-receiver/        # SDR Signal Capture
├── red-team/               # Adversary Emulation
│   ├── attack-engine/      # Hybrid Web/SSH Attacker
│   ├── password-auditor/   # Credential Cracker
│   ├── c2-beacon/          # Malware Implant
│   └── ... (See Current_Status for full list)
├── blue-team/              # Defensive Operations
│   ├── honeypot-ssh/       # Paramiko Trap
│   ├── blue-sentinel/      # SIEM Engine
│   └── ids-suricata/       # Network Detection
├── target/                 # The Battlefield
│   ├── public-web/         # [Port 8080] Vulnerable App
│   └── internal-infra/     # Simulated File Servers
├── intel/                  # Threat Intelligence Feeds
└── grc/                    # Compliance & Reporting
```

## 4. Network & Ports
*   **Internal Network:** `nebulax-net` (Docker Bridge)
*   **External Access:**
    *   `localhost:3000` -> Dashboard
    *   `localhost:8000` -> Core API
    *   `localhost:8080` -> Target Web App
    *   `localhost:5432` -> PostgreSQL (Exposed for debugging)
    *   `localhost:6379` -> Redis (Exposed for debugging)

## 5. Development Constraints
*   **Docker Only:** The host environment is treated as ephemeral. All state must persist in Docker Volumes (`nebulax-db-data`).
*   **Python 3.10+:** Standard for all backend services.
*   **Node.js 18+:** Standard for Dashboard.

