# NebulaX Threat Models

**Related docs:** [ORBITGUARD.md](ORBITGUARD.md) — space War Detector and space-cyber fusion | [ARCHITECTURE.md](ARCHITECTURE.md) — event schema and API reference | [SERVICES.md](SERVICES.md) — per-service behavior | [QUICKSTART.md](QUICKSTART.md) — running exercises

---

## Overview

NebulaX models a coordinated, multi-vector attack against a fictional defense contractor, Astra Dynamics. The threat scenario combines state-sponsored cyber intrusion techniques with orbital domain operations, reflecting the real-world convergence of space and cyber warfare.

This document covers: the MITRE ATT&CK techniques implemented, the intentional vulnerabilities in the target environment, per-service attack and detection narratives, and structured exercise playbooks for red and blue team operators.

---

## Threat Scenario: Astra Dynamics Under Siege

**Victim organization:** Astra Dynamics (fictional defense contractor)
**Threat actors:** APT29 (Russia), APT41 (China), Lazarus Group (DPRK) — simulated
**Attack objectives:**
1. Credential theft and privilege escalation on enterprise systems
2. Lateral movement to ground station infrastructure
3. Data exfiltration to simulated C2 infrastructure
4. Ransomware deployment for disruption/extortion
5. Orbital domain awareness — satellite proximity interference, GNSS jamming

---

## MITRE ATT&CK Coverage

### Tactics and Techniques Implemented

| MITRE ID | Technique | Service | Event Type |
|----------|-----------|---------|------------|
| T1046 | Network Service Discovery | `vuln-scanner` | `VULN_REPORT` |
| T1059 | Command and Scripting Interpreter | `apt-emulator` | `COMMAND_EXECUTED` |
| T1071 | Application Layer Protocol (C2) | `c2-beacon` | `NETWORK_FLOW` |
| T1078 | Valid Accounts | `attack-engine` (SQLi auth bypass) | `EXPLOIT_SUCCESS` |
| T1110 | Brute Force | `attack-engine` | `AUTH_FAILURE` |
| T1110.004 | Credential Stuffing (Offline) | `password-auditor` | `CREDENTIAL_CRACKED` |
| T1190 | Exploit Public-Facing Application | `web-injector` | `WEB_TRAFFIC` |
| T1486 | Data Encrypted for Impact | `ransomware-sim` | `FILE_ENCRYPTED` |
| T1491 | Defacement / Ransom Note | `ransomware-sim` | `RANSOM_NOTE` |
| T1595 | Active Scanning | `vuln-scanner` | `VULN_REPORT` |

### Detection Coverage (Blue Team)

| Detected Technique | Detecting Service | Detection Method |
|--------------------|------------------|-----------------|
| T1046 | `net-watchdog` | Correlates `VULN_REPORT` events with vulnerable port exposure |
| T1059 | `honeypot` | Logs all commands executed in deception shell |
| T1071 | `net-watchdog` | Flow size threshold — exfil events > 1MB trigger alert |
| T1078 | `blue-sentinel` | Correlates `EXPLOIT_SUCCESS` with prior `AUTH_FAILURE` events |
| T1110 | `honeypot`, `ids-suricata` | SSH root login pattern matching |
| T1190 | `ids-suricata` | Log4j RCE, SQL injection pattern matching |
| T1486 | `edr-agent` | Ransomware-like process behavior patterns |
| T1059 (PowerShell) | `edr-agent` | PowerShell `-enc` flag detection |

---

## Intentional Vulnerabilities: Target Environment

The target environment contains deliberate weaknesses for controlled exploitation exercises. These are isolated within the `nebulax-net` Docker network.

### Public Web Portal (`nebulax-target-web`)

**Vulnerability 1: SQL Injection in Login**

The login endpoint directly interpolates user input into a SQL query:

```python
# services/target/public-web/app.py
query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
```

**Exploitation:**
- Payload: `admin' --` (username), any value (password)
- Effect: Bypasses authentication, logs in as `admin`
- Flag: `flag{astra_master_key_xyz}` (admin's stored password)

**Vulnerability 2: Insecure Secret Key**
- Flask session key: `astra_dynamics_insecure_key`
- Enables session cookie forgery with known key

**Seeded credentials:**

| Username | Password |
|----------|----------|
| `admin` | `flag{astra_master_key_xyz}` |
| `guest` | `guest` |

---

### Ground Station (`nebulax-ground-sim`)

**Vulnerability 1: Hardcoded Credentials**
- Username: `admin`
- Password: `solarwinds123`
- Access: `POST /api/login` returns a JWT

**Vulnerability 2: Weak JWT Secret**
- Secret: `ground_station_secret_key_123`
- Algorithm: HS256
- Enables token forgery with known secret

**Vulnerability 3: IDOR on Telemetry Endpoint**
- `GET /api/telemetry` — no per-user authorization check
- Any valid token retrieves full satellite telemetry data

**No rate limiting** on login endpoint — brute force is unthrottled.

---

### SSH Honeypot (`nebulax-honeypot`)

**Design intent:** The honeypot is not a vulnerability but a deception asset. It intentionally accepts ALL login credentials to maximize attacker dwell time and intelligence collection.

**Interactive shell simulation:**
- Responds to `ls`, `pwd`, `whoami` with convincing fake output
- All commands are logged as `COMMAND_EXECUTED` events
- Credential captures are logged as `AUTH_FAILURE` (initial attempt) and `AUTH_SUCCESS` (shell gained)
- Password captures feed the `password-auditor` offline cracking pipeline

---

## Red Team Service Narratives

### Attack Engine — Initial Access and Lateral Movement

The attack engine is the primary initial access tool. It runs two attack vectors in alternating cycles (10-second intervals):

**Vector 1: SSH Brute Force**
- Target: `nebulax-honeypot:2222`
- Credential list: Randomized from common username/password wordlists
- Trigger: Each attempt generates an `AUTH_FAILURE` event
- Success condition: The honeypot always accepts — `AUTH_SUCCESS` generated on first attempt

**Vector 2: SQL Injection**
- Target: `nebulax-target-web:5000/login`
- Payload: `admin' --` (username), `x` (password)
- Trigger: `EXPLOIT_SUCCESS` event on HTTP 200 response
- Effect: Demonstrates T1078 (auth bypass via injection)

---

### APT Emulator — Kill Chain Simulation

Simulates the progression through Lockheed Martin Kill Chain stages over successive cycles (20-second intervals, 50% fire rate):

```
Reconnaissance → Weaponization → Delivery → Exploitation
→ Installation → Command & Control → Actions on Objectives
```

Each stage fires a `COMMAND_EXECUTED` event with the current stage name and a simulated command payload. This allows blue team analysts to observe an adversary progressing through the kill chain in the event log.

---

### C2 Beacon — Exfiltration Simulation

Simulates a compromised endpoint beaconing to known state-sponsored C2 infrastructure:

| IP Address | Attribution | APT Group |
|------------|------------|-----------|
| `185.100.84.21` | Russia | APT29 (Cozy Bear) |
| `45.122.99.12` | China | APT41 (Double Dragon) |
| `103.15.66.88` | North Korea | Lazarus Group |

**Beacon behavior (10–30 second jitter):**
- 90% of beacons: small heartbeat (200–500 bytes)
- 10% of beacons: large exfiltration burst (50 KB – 5 MB)

The jitter pattern mimics real APT tradecraft — randomized intervals to evade time-based detection rules.

**Detection hook:** The `net-watchdog` service triggers on `NETWORK_FLOW` events exceeding 1 MB, generating a `THREAT_DETECTED` alert for the large exfiltration beacons.

---

### Ransomware Simulator — Impact Phase

Simulates the impact phase of a ransomware campaign against three Astra Dynamics endpoints:

- `HR-Workstation`
- `CEO-Laptop`
- `Finance-Server`

**Per-cycle behavior (20–60 second random intervals):**
1. Selects 5–50 random files with extensions: `.docx`, `.xlsx`, `.pdf`, `.jpg`, `.sql`
2. Generates `FILE_ENCRYPTED` event (CRITICAL severity) per file — MITRE T1486
3. Drops a ransom note with a simulated Bitcoin wallet address — MITRE T1491

The variable interval and random file count simulate the non-deterministic behavior of real ransomware, ensuring blue team detection rules cannot rely on timing.

---

### Vulnerability Scanner — Reconnaissance

Performs Nmap-style port scanning against:
- `nebulax-target-web` (ports 22, 80, 443, 5000, 8080)
- `nebulax-honeypot` (ports 22, 2222)

Each open port discovered fires a `VULN_REPORT` event (MEDIUM severity) tagged with MITRE T1046. The `net-watchdog` correlates these with subsequent exploitation events.

---

### Password Auditor — Credential Harvesting

This service closes the loop between the honeypot and the offline cracking pipeline:

1. Polls `GET /events/recent?event_type=AUTH_FAILURE` every cycle
2. Extracts captured passwords from honeypot login events
3. Compares against a `rockyou_sample.txt` wordlist
4. On match: fires `CREDENTIAL_CRACKED` event (HIGH severity, T1110.004)

This demonstrates that honeypot credential captures have real downstream intelligence value — attackers may use harvested credentials against other systems.

---

## Blue Team Service Narratives

### SSH Honeypot — Deception as Code

The honeypot is the primary intelligence collection layer. Its architecture:

- **Paramiko-based SSH server** listening on port 2222
- Accepts all credentials unconditionally
- Presents a convincing interactive shell with fake filesystem responses
- Every login and command is structured and published to Core

**Intelligence output:** Credential pairs, command sequences, and dwell time data — all available in the event log for analysis and the password auditor pipeline.

---

### Blue Sentinel — Rule-Based SIEM

A lightweight rule engine that correlates events from the stream. Currently implemented rules:

- **Rule 1:** On `EXPLOIT_SUCCESS` → generate `THREAT_DETECTED` (CRITICAL) with attacker IP
- Correlation: Cross-references IP address from exploit event with prior auth failure events

This is the simplest form of SIEM correlation — a detected exploit triggers an alert that links back to the reconnaissance and brute force activity from the same source.

---

### IDS Suricata — Signature Detection Simulation

Simulates the Suricata IDS with ET Open ruleset signatures. Fires `THREAT_DETECTED` events matching real-world signature categories:

| Signature | Category | Severity |
|-----------|----------|----------|
| Cobalt Strike beacon | Command-and-Control | HIGH |
| Apache Log4j RCE (CVE-2021-44228) | Exploitation | CRITICAL |
| Nmap/NSE scanner fingerprint | Reconnaissance | MEDIUM |
| SSH root login attempt | Credential Access | HIGH |

**Fire rate:** 50% probability per 10-second cycle. This simulates the noise of a real IDS feed — not every cycle generates an alert.

---

### EDR Agent — Endpoint Behavioral Detection

Monitors for endpoint-level behavioral indicators:

| Behavior | MITRE | Severity |
|----------|-------|----------|
| PowerShell `-enc` flag (encoded command) | T1059.001 | HIGH |
| LSASS memory access (credential dumping) | T1003.001 | CRITICAL |
| Unsigned driver load | T1014 | HIGH |
| Registry Run key persistence | T1547.001 | HIGH |

**Fire rate:** 50% probability per 15-second cycle across monitored assets (`workstation-01`, `server-main`, `executive-laptop`).

---

### Net Watchdog — Exfiltration Detection

Two primary detection rules:

**Rule 1: Large data exfiltration**
- Trigger: `NETWORK_FLOW` event with `bytes_transferred > 1,000,000` (1 MB)
- Alert: `THREAT_DETECTED` (HIGH) — "Potential data exfiltration detected"
- Catches: C2 beacon large exfiltration bursts (10% of beacon cycles)

**Rule 2: Vulnerable service exposure**
- Trigger: `VULN_REPORT` event from the vulnerability scanner
- Alert: `THREAT_DETECTED` (MEDIUM) — correlates open port with asset
- Catches: Reconnaissance phase activity

---

### Network Forensics — Automated Case Generation

Monitors the event stream for `THREAT_DETECTED` events and automatically creates forensic investigation summaries:

1. Collects all related events for the triggering alert (same IP, same time window)
2. Constructs an investigation summary with timeline, asset, and technique data
3. Submits a `FORENSIC_CASE` event to Core with the compiled case file

This demonstrates automated SOC triage — reducing analyst workload by pre-correlating evidence at the time of detection.

---

## Exercise Playbooks

### Red Team Exercise: Initial Access to Exfiltration

**Objective:** Demonstrate a complete attack lifecycle against Astra Dynamics, from reconnaissance through data exfiltration.

**Step 1 — Reconnaissance (T1046)**
```bash
docker compose --profile red up vuln-scanner
# Monitor: GET http://localhost:8000/events/recent?event_type=VULN_REPORT
```
Observe open ports being discovered on `target-web` and `honeypot`.

**Step 2 — Initial Access (T1190)**
```bash
# The attack-engine fires SQL injection automatically
# Verify at: http://localhost:8080/login
# Manual payload: username = admin' --, password = anything
```

**Step 3 — Credential Access (T1110, T1110.004)**
```bash
# Attack engine brute-forces honeypot SSH (port 2222)
# Password auditor harvests and cracks credentials
# Monitor: GET http://localhost:8000/events/recent?event_type=CREDENTIAL_CRACKED
```

**Step 4 — C2 and Exfiltration (T1071)**
```bash
# C2 beacon runs on profile red
# Large exfils (> 1MB) are visible in NETWORK_FLOW events
# Monitor: GET http://localhost:8000/events/recent?event_type=NETWORK_FLOW
```

**Step 5 — Impact (T1486)**
```bash
# Ransomware sim fires on profile red
# Monitor: GET http://localhost:8000/events/recent?event_type=FILE_ENCRYPTED
```

---

### Blue Team Exercise: Detection and Response

**Objective:** Identify and correlate all phases of a multi-stage attack using the blue team toolstack.

**Phase 1 — Alert Triage**
```bash
docker compose --profile blue up
# Dashboard: http://localhost:3000/blue
# Watch for THREAT_DETECTED events from blue-sentinel, ids-suricata, edr-agent
```

**Phase 2 — Correlation**
```bash
# Query events by IP to correlate recon → exploit → exfil
GET http://localhost:8000/events/recent?limit=100
# Look for same related_ip appearing in VULN_REPORT → AUTH_FAILURE → EXPLOIT_SUCCESS
```

**Phase 3 — Forensics**
```bash
# Net-forensics auto-generates FORENSIC_CASE events
# Each case contains the correlated evidence timeline
GET http://localhost:8000/events/recent?event_type=FORENSIC_CASE
```

**Phase 4 — DEFCON Assessment**
```bash
GET http://localhost:8000/game/state
# Track red score progression and DEFCON level
# Objective: Keep DEFCON above 3 by detecting exploits before they score
```

---

### Space + Cyber Fusion Exercise

**Objective:** Identify correlations between orbital threat indicators and simultaneous ground-based cyber attacks.

```bash
docker compose --profile full up
# Navigate to http://localhost:3000/space
```

**Scenario:** A GNSS jamming event is detected by the Space War Detector (GNSSWatcher module). Simultaneously, the attack engine launches a SQL injection against the ground station. The fusion center operator must:

1. Observe the GNSS jamming alert in the Space Strategic Analysis Panel
2. Correlate with the `AUTH_FAILURE` events on the ground station
3. Assess whether the ground station is being targeted while space defenses are degraded
4. Determine DEFCON level from the combined space escalation score + cyber red score

This exercise demonstrates the core thesis of NebulaX: space and cyber attacks are coordinated, and a single-domain view misses the combined threat picture.

---

## GRC Integration

### Compliance Mapping (policy-mapper)

The `policy-mapper` service maps alert events to compliance framework obligations:

| Event Type | Framework | Clause |
|------------|-----------|--------|
| `THREAT_DETECTED` (CRITICAL) | GDPR | Article 33 — 72-hour breach notification |
| `CREDENTIAL_CRACKED` | NIST | IR-6 — Incident reporting |
| `EXPLOIT_SUCCESS` | CFAA | 18 U.S.C. § 1030 — Unauthorized access |
| `FILE_ENCRYPTED` | NIST | CP-2 — Contingency plan activation |

### Automated Incident Reporting (incident-reporter)

The `incident-reporter` generates structured incident reports on a 45-second cycle (40% fire rate), simulating a CISO notification workflow:

```json
{
  "report_id": "IR-2025-00142",
  "status": "SUBMITTED",
  "recipients": ["CISO"],
  "summary": "Automated incident report generated from threat event stream"
}
```

---

## Space Threat Models

### Space War Detector: Six-Module Architecture

The Space War Detector runs as an integrated subsystem of the space tracker, executing every 60-second telemetry cycle.

| Module | Threat Modeled | Indicator |
|--------|---------------|-----------|
| `ManeuverDetector` | Evasive orbital maneuver by adversary satellite | Sudden TLE delta-V change |
| `ProximityDetector` | Kinetic/electronic interference via close approach | Satellite pair distance threshold |
| `DebrisListener` | Intentional debris creation (ASAT test) | Debris object count spike |
| `GNSSWatcher` | GPS/GLONASS jamming affecting ground operations | Signal anomaly in satellite telemetry |
| `LaunchMonitor` | Surprise military satellite launch | New TLE objects with no prior SATCAT entry |
| `GEOSentinel` | Co-orbital maneuvering near high-value GEO assets | GEO slot proximity breach |

**Output fusion:**

Each module returns a binary alert and a severity weight. The BehavioralClassifier fuses all six signals into:
- **Escalation score:** 0–100 (weighted sum of active alerts)
- **DEFCON level:** 5–1 (thresholded from escalation score)
- **Alerts list:** Active alert names for dashboard display

The space DEFCON feeds into the combined game state DEFCON alongside the cyber red/blue score.

### ML Country Attribution

The satellite country attribution model provides intelligence on which nation-state operates each tracked object, relevant to assessing the threat context of proximity and maneuver events.

**Training data:** SATCAT metadata from Space-Track (country field per NORAD ID)
**Features:** Orbital inclination + apogee altitude
**Model:** RandomForestClassifier (scikit-learn)
**Training frequency:** At service startup, with periodic refresh

The model's predictions are displayed alongside verified SATCAT metadata on the dashboard. Divergence between predicted and verified country may indicate satellite ownership obscuration — a potential intelligence indicator.
