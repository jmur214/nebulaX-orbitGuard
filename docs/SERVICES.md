# Service Catalog

Complete reference for all 26+ NebulaX microservices. Each entry covers purpose, behavior, event output, configuration, and inter-service dependencies.

For the system-level architecture and event schema, see [ARCHITECTURE.md](ARCHITECTURE.md).
For in-depth documentation of the space domain services, see [ORBITGUARD.md](ORBITGUARD.md).

---

## Core Infrastructure

### core-api

**Container:** `nebulax-core`
**Port:** `8000`
**Profile:** All profiles

The central hub of the platform. All services communicate exclusively through this API — there is no direct service-to-service communication.

**Responsibilities:**
- Event ingestion and persistence (`POST /events/ingest`)
- Event querying (`GET /events/recent`)
- Game state calculation (`GET /game/state`)
- On-demand orbit computation (`GET /satellite/orbit`)

**Dependencies:** `postgres`, `redis`

**Key files:** `services/core/main.py`, `services/core/orbit_computer.py`

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full API reference.

---

### postgres

**Container:** `nebulax-db`
**Port:** `5432`
**Image:** `postgres:15-alpine`
**Profile:** All profiles

PostgreSQL 15 serves as the event lake. All events are persisted here with JSONB payloads for flexible querying. The database is initialized with the `nebulax_core` database and a single `events` table.

**Health check:** `pg_isready -U admin -d nebulax_core` (5s interval, 5 retries)

---

### redis

**Container:** `nebulax-bus`
**Port:** `6379`
**Image:** `redis:7-alpine`
**Profile:** All profiles

Redis serves as the event bus for pub/sub and as an optional cache for orbit path computations (currently disabled for debugging). It is also available for future use as a real-time event stream alongside the PostgreSQL persistence layer.

---

### dashboard

**Container:** `nebulax-dashboard-v2`
**Port:** `3000`
**Profile:** `core`, `full`
**Memory limit:** 2 GB

Next.js 14 frontend with Cesium.js integration. Polls `GET /events/recent` every 2 seconds per page. Turbopack is enabled for faster development compilation.

**Pages:**

| Route | Purpose | Data filter |
|-------|---------|-------------|
| `/space` | Orbital visualization, Space War Detector | `?team=space` |
| `/red` | Red team activity and kill chain progress | `?team=red` |
| `/blue` | Blue team alerts and detection log | `?team=blue` |
| `/fusion` | Combined multi-domain threat picture | all events |
| `/login` | Persona-based authentication | — |

**Key components:** `SatelliteGlobe.js` (Cesium orbit visualization), `space.js` (Space Command page)

**Key files:** `services/dashboard/src/pages/space.js`, `services/dashboard/src/components/SatelliteGlobe.js`

---

## Space Domain (OrbitGuard)

For comprehensive documentation of the space domain, see [ORBITGUARD.md](ORBITGUARD.md).

### space-tracker

**Container:** `nebulax-space-tracker`
**Profile:** `space`, `full`
**Memory limit:** 128 MB
**Cycle interval:** 60 seconds

The primary OrbitGuard sensor. Fetches real NORAD TLE data, propagates orbits via Skyfield SGP4, runs ML country attribution, and executes the Space War Detector on every cycle.

**Environment variables:**

| Variable | Default | Required |
|----------|---------|----------|
| `CORE_API_URL` | `http://nebulax-core:8000/events/ingest` | Yes |
| `SPACETRACK_USER` | — | No (Celestrak fallback) |
| `SPACETRACK_PASS` | — | No (Celestrak fallback) |

**Events published:**
- `TLE_UPDATE` — one per tracked satellite per cycle, includes full orbital state and war_metrics
- `FINGERPRINT_UPDATE` — orbital cluster visualization (base64 matplotlib PNG)

**Startup behavior:** Trains the RandomForest country attribution classifier before the first telemetry cycle. First cycle takes slightly longer.

**Key files:** `services/space-guard/tracker/main.py`, `services/space-guard/tracker/war_detector/`

---

### ground-station

**Container:** `nebulax-ground-sim`
**Port:** `5001` (→ internal `5000`)
**Profile:** `space`, `full`

Intentionally vulnerable Flask application simulating a satellite ground station.

**Vulnerabilities:** Hardcoded credentials (`admin / solarwinds123`), predictable JWT secret (`ground_station_secret_key_123`), no rate limiting, IDOR on telemetry endpoint.

**Endpoints:**
- `POST /api/login` — JWT authentication (accepts hardcoded credentials)
- `GET /api/telemetry` — Satellite telemetry data (requires any valid JWT)
- `GET /api/command` — Command interface stub

**Events published:**
- `AUTH_FAILURE` on failed login
- `AUTH_SUCCESS` on successful login

---

### rf-receiver

**Container:** `nebulax-rf-receiver`
**Profile:** `space`, `full`

Simulates a software-defined radio receiver monitoring the UHF satellite downlink band (400–450 MHz). Fires `RF_SIGNAL_CAPTURED` events with ~30% probability per 30-second cycle.

**Events published:**
- `RF_SIGNAL_CAPTURED` — frequency, signal strength (dBm), modulation, duration

---

## Red Team

### attack-engine

**Container:** `nebulax-red-attacker`
**Profile:** `red`, `full`
**Memory limit:** 128 MB
**Cycle interval:** 10 seconds

The primary initial access tool. Alternates between SSH brute force and SQL injection attacks.

**Attack 1: SSH Brute Force (T1110)**
- Target: `nebulax-honeypot:2222`
- Credential pool: Random selection from common username/password wordlists
- Triggers: `AUTH_FAILURE` events from the honeypot

**Attack 2: SQL Injection (T1190)**
- Target: `nebulax-target-web:5000/login`
- Payload: `admin' --` (username), `x` (password)
- On HTTP 200: publishes `EXPLOIT_SUCCESS`

**Dependencies:** `honeypot`, `target-web`

---

### apt-emulator

**Container:** `nebulax-apt-emulator`
**Profile:** `red`, `full`
**Memory limit:** 128 MB
**Cycle interval:** 20 seconds (50% fire rate)

Simulates kill chain stage progression.

**Stages (cycled in order):**
Reconnaissance → Weaponization → Delivery → Exploitation → Installation → C2 → Actions on Objectives

**Events published:**
- `COMMAND_EXECUTED` (HIGH) — includes current stage name and simulated command payload, tagged MITRE T1059

---

### ransomware-sim

**Container:** `nebulax-ransomware`
**Profile:** `red`, `full`
**Memory limit:** 128 MB
**Cycle interval:** 20–60 seconds (random)

Simulates the impact phase of a ransomware campaign against three Astra Dynamics endpoints: `HR-Workstation`, `CEO-Laptop`, `Finance-Server`.

**Behavior per cycle:**
1. Selects 5–50 random files (`.docx`, `.xlsx`, `.pdf`, `.jpg`, `.sql`)
2. Publishes `FILE_ENCRYPTED` (CRITICAL) per file — T1486
3. Publishes `RANSOM_NOTE` (HIGH) with simulated Bitcoin wallet — T1491

The random interval and file count simulate non-deterministic ransomware behavior to prevent time-based blue team detection shortcuts.

---

### web-injector

**Container:** `nebulax-web-injector`
**Profile:** `red`, `full`
**Memory limit:** 128 MB
**Cycle interval:** 15 seconds (50% fire rate)

Sends web exploitation payloads to the target portal.

**Payloads (cycled):**
- `' OR 1=1 --` (SQL injection)
- `<script>alert(1)</script>` (XSS)
- `../../etc/passwd` (path traversal)

**Events published:**
- `WEB_TRAFFIC` (MEDIUM) — includes payload type and HTTP response code, tagged T1190

---

### password-auditor

**Container:** `nebulax-password-auditor`
**Profile:** `red`, `full`
**Memory limit:** 128 MB

Closes the loop between honeypot credential captures and offline cracking.

**Workflow:**
1. Polls `GET /events/recent?event_type=AUTH_FAILURE` every cycle
2. Extracts passwords captured by the honeypot from event payloads
3. Compares against `rockyou_sample.txt` wordlist
4. On match: publishes `CREDENTIAL_CRACKED` (HIGH), tagged T1110.004

---

### vuln-scanner

**Container:** `nebulax-vuln-scanner`
**Profile:** `red`, `full`
**Memory limit:** 256 MB (Nmap requires more RAM)
**Cycle interval:** 60 seconds

Nmap-based network reconnaissance against target services.

**Targets:**
- `nebulax-target-web` — ports 22, 80, 443, 5000, 8080
- `nebulax-honeypot` — ports 22, 2222

**Events published:**
- `VULN_REPORT` (MEDIUM) per open port — tagged T1046

---

### c2-beacon

**Container:** `nebulax-c2-beacon`
**Profile:** `red`, `full`
**Memory limit:** 128 MB
**Beacon interval:** 10–30 seconds (randomized jitter)

Simulates a compromised endpoint beaconing to known state-sponsored C2 infrastructure.

**Simulated C2 operators:**

| IP | Country | Group |
|----|---------|-------|
| `185.100.84.21` | Russia | APT29 |
| `45.122.99.12` | China | APT41 |
| `103.15.66.88` | DPRK | Lazarus |

**Beacon pattern:**
- 90%: small heartbeat (200–500 bytes)
- 10%: large exfiltration (50 KB – 5 MB)

**Events published:**
- `NETWORK_FLOW` (MEDIUM/HIGH) — includes destination IP, bytes transferred, tagged T1071

---

## Blue Team

### honeypot

**Container:** `nebulax-honeypot`
**Port:** `2222`
**Profile:** `blue`, `red`, `full`

High-interaction SSH deception shell built with Paramiko. Accepts all login credentials unconditionally. Presents a convincing interactive shell environment.

**Fake shell responses:**
- `ls` → fake filesystem listing
- `pwd` → `/home/admin`
- `whoami` → `admin`

**Events published:**
- `AUTH_FAILURE` (MEDIUM) — captures username and password on every attempt
- `AUTH_SUCCESS` (CRITICAL) — when attacker gains the shell
- `COMMAND_EXECUTED` (HIGH) — per command issued in the deception shell

The credential captures from `AUTH_FAILURE` events feed the `password-auditor`'s offline cracking pipeline.

---

### blue-sentinel

**Container:** `nebulax-blue-sentinel`
**Profile:** `blue`, `full`
**Memory limit:** 128 MB

Rule-based detection engine that correlates events from the stream.

**Active rules:**
- **Rule 1:** On `EXPLOIT_SUCCESS` → generate `THREAT_DETECTED` (CRITICAL), correlate source IP with prior `AUTH_FAILURE` events from the same IP

**Events published:**
- `THREAT_DETECTED` (CRITICAL) — includes correlated evidence chain

---

### ids-suricata

**Container:** `nebulax-ids-suricata`
**Profile:** `blue`, `full`
**Cycle interval:** 10 seconds (50% fire rate)

Simulates Suricata IDS alerts using Emerging Threats (ET) Open ruleset signatures.

**Simulated signatures:**

| Signature | Category | Severity |
|-----------|----------|----------|
| Cobalt Strike C2 beacon | C2 | HIGH |
| Apache Log4j RCE (CVE-2021-44228) | Exploitation | CRITICAL |
| Nmap/NSE scanner fingerprint | Reconnaissance | MEDIUM |
| SSH root login attempt | Credential Access | HIGH |

**Events published:**
- `THREAT_DETECTED` (HIGH/CRITICAL) — includes rule name and category

---

### edr-agent

**Container:** `nebulax-edr-agent`
**Profile:** `blue`, `full`
**Cycle interval:** 15 seconds (50% fire rate)

Simulates an endpoint detection and response agent monitoring `workstation-01`, `server-main`, and `executive-laptop`.

**Monitored behaviors:**

| Behavior | MITRE | Severity |
|----------|-------|----------|
| PowerShell with `-enc` flag (encoded command) | T1059.001 | HIGH |
| LSASS process memory access | T1003.001 | CRITICAL |
| Unsigned kernel driver load | T1014 | HIGH |
| Registry Run key write (persistence) | T1547.001 | HIGH |

**Events published:**
- `THREAT_DETECTED` (HIGH/CRITICAL) — includes asset name and behavior description

---

### net-watchdog

**Container:** `nebulax-net-watchdog`
**Profile:** `blue`, `full`
**Memory limit:** 128 MB

Network flow analyzer with exfiltration and reconnaissance detection.

**Detection rules:**
1. `NETWORK_FLOW` event with `bytes_transferred > 1,000,000` → `THREAT_DETECTED` (HIGH): "Potential data exfiltration detected"
2. `VULN_REPORT` event → `THREAT_DETECTED` (MEDIUM): correlates open port with asset exposure

**Events published:**
- `THREAT_DETECTED` (HIGH/MEDIUM)

---

### net-forensics

**Container:** `nebulax-net-forensics`
**Profile:** `blue`, `full`
**Memory limit:** 128 MB

Automated forensic case file generation. Monitors for `THREAT_DETECTED` events and assembles correlated evidence.

**Workflow:**
1. Receive `THREAT_DETECTED` event
2. Query related events: same source IP, same time window, same asset
3. Assemble investigation summary with timeline, asset, and technique data
4. Publish `FORENSIC_CASE` (INFO) containing the compiled case

**Events published:**
- `FORENSIC_CASE` — structured investigation summary

---

## Target Environment

### target-web

**Container:** `nebulax-target-web`
**Port:** `8080` (→ internal `5000`)
**Profile:** `target`, `red`, `full`

Intentionally vulnerable Flask web application. The primary target for the attack-engine's SQL injection attack vector.

**Vulnerabilities:**
- **SQL injection:** Login query directly interpolates user input:
  ```python
  query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
  ```
- **Insecure session key:** `astra_dynamics_insecure_key`
- **In-memory SQLite DB** with seeded credentials:
  - `admin / flag{astra_master_key_xyz}`
  - `guest / guest`

**Routes:**
- `GET /` — Login form
- `POST /login` — Vulnerable authentication endpoint
- `GET /dashboard` — Role-based user dashboard

**Events published:**
- `WEB_TRAFFIC` on each login attempt

---

### identity-manager

**Container:** `nebulax-identity-manager`
**Profile:** `target`, `full`
**Cycle interval:** 20 seconds (50% fire rate)

Simulates LDAP/Active Directory authentication events. Generates realistic `AUTH_FAILURE` events with Faker-generated usernames and email addresses, simulating enterprise user authentication noise.

**Events published:**
- `AUTH_FAILURE` (MEDIUM) — fake user credentials, reason: `BAD_PASSWORD`

---

### internal-infra

**Container:** `nebulax-internal-infra`
**Profile:** `target`, `full`
**Cycle interval:** 15 seconds (60% fire rate)

Simulates SMB file share network traffic from internal enterprise infrastructure.

**Events published:**
- `NETWORK_FLOW` (LOW) — protocol: `SMB`, action: `FILE_ACCESS`

---

## GRC & Compliance

### incident-reporter

**Container:** `nebulax-incident-reporter`
**Profile:** `grc`, `full`
**Cycle interval:** 45 seconds (40% fire rate)

Generates structured incident reports addressed to the CISO, simulating a real-time SOC notification workflow.

**Events published:**
- `INFO` — report ID, status (`SUBMITTED`), recipients (`CISO`), summary

---

### policy-mapper

**Container:** `nebulax-policy-mapper`
**Profile:** `grc`, `full`
**Cycle interval:** 30 seconds

Maps alert events to compliance framework clauses.

**Framework coverage:**

| Event | Framework | Clause |
|-------|-----------|--------|
| `THREAT_DETECTED` (CRITICAL) | GDPR | Article 33 (72-hour notification) |
| `CREDENTIAL_CRACKED` | NIST | IR-6 (Incident reporting) |
| `EXPLOIT_SUCCESS` | CFAA | 18 U.S.C. § 1030 |
| `FILE_ENCRYPTED` | NIST | CP-2 (Contingency plan) |

**Events published:**
- `INFO` — includes framework, clause, and triggering event reference

---

## Threat Intelligence

### cve-feeder

**Container:** `nebulax-cve-feeder`
**Profile:** `intel`, `full`
**Cycle interval:** 20 seconds (50% fire rate)

Simulates real-time vulnerability intelligence feed ingestion.

**Simulated CVEs:**
- `CVE-2024-3094` (XZ Utils backdoor)
- `CVE-2023-44487` (HTTP/2 Rapid Reset)
- `CVE-2021-44228` (Log4Shell)

**Events published:**
- `VULN_REPORT` (HIGH) — CVE ID, CVSS score, affected component

---

### ioc-manager

**Container:** `nebulax-ioc-manager`
**Profile:** `intel`, `full`
**Cycle interval:** 30 seconds (40% fire rate)

Simulates Indicators of Compromise synchronization from a threat intelligence platform (AlienVault OTX).

**Events published:**
- `INFO` — IOC count, source (`AlienVault OTX`), sync status
