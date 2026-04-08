# NebulaX Resume Assets

**Project:** NebulaX OrbitGuard — Cyber-Physical Fusion Range
**Context:** Personal research project. Fully operational, containerized platform.
**Scale:** 26+ microservices, 7 operational domains, real satellite data, 3D visualization frontend.

This document contains technically precise achievement statements and skills extracted directly from the implemented codebase. These are suitable for use in resumes, portfolio write-ups, and interview preparation.

---

## Achievement Statements

### Space Systems & Orbital Mechanics

- Built a real-time orbital dynamics engine in Python using Skyfield's SGP4 propagation model. The engine ingests live NORAD Two-Line Element sets from the Space-Track API (with Celestrak fallback), propagates 90-minute orbit paths at 2-minute intervals, and computes topocentric look-angles (azimuth, elevation, slant range) for a configurable ground station.

- Engineered an on-demand orbit computation API endpoint (`GET /satellite/orbit`) backed by a PostgreSQL JSONB event store. TLE data is retrieved from the most recent telemetry event for the requested satellite, propagated through Skyfield, and returned as a coordinate array consumed by the 3D Cesium frontend.

- Implemented a six-module Space War Detector that runs every telemetry cycle alongside satellite tracking. Modules assess orbital maneuvers, satellite proximity (rendezvous and proximity operations), space debris spikes, GNSS jamming indicators, launch surge detection, and GEO belt anomalies. A behavioral fusion classifier aggregates module outputs into a DEFCON level (1–5) and weighted escalation score (0–100).

- Deployed a RandomForest ML classifier (scikit-learn) that trains at runtime on live orbital parameters — inclination and apogee — against SATCAT country ground truth. The model predicts operator nation-state for every tracked satellite and outputs a confidence score alongside verified metadata, enabling attribution analysis for proximity and maneuver events.

- Designed and rendered a 3D orbital visualization using Cesium.js and the Resium React wrapper. Satellites are displayed as live-updating, country-coded point entities on a globe. On selection, the frontend requests the orbit path from the Core API and renders it as a Cartesian3 polyline, converting altitude from kilometers to meters for Cesium's coordinate system.

---

### Event-Driven Systems Architecture

- Architected a universal event ingestion system in which 26+ microservices communicate exclusively through a single FastAPI endpoint (`POST /events/ingest`). Events are persisted to PostgreSQL as JSONB payloads with indexed metadata fields, enabling efficient cross-service correlation queries without inter-service dependencies.

- Designed a schema-enforced universal event model covering `event_meta` (UUID, timestamp, origin module, type, severity), `context` (IP, asset ID, MITRE ATT&CK technique, compliance tag), and a flexible `payload` object. This schema is shared across Python (FastAPI/Pydantic) and JavaScript (Next.js) services with consistent field naming.

- Built a live game state engine as a FastAPI endpoint that computes red/blue team scores and DEFCON escalation level by aggregating typed events from the PostgreSQL event ledger. Scores are calculated through a SQL aggregation query at request time — no separate state store required.

- Implemented a fully async Python backend using FastAPI, asyncio, and asyncpg throughout the Core API and all Python microservices, supporting concurrent event ingestion from 26+ simultaneous producers without blocking.

---

### Offensive Security Engineering

- Implemented ten MITRE ATT&CK techniques across seven automated red team services, covering the full kill chain from reconnaissance (T1046) through impact (T1486, T1491). Each service publishes structured events with MITRE technique IDs embedded in the `context` field.

- Built an offline credential harvesting pipeline in which the SSH honeypot captures attacker-submitted passwords, publishes them as structured events, and a downstream password auditor service polls the event stream, cross-references credentials against a wordlist, and reports confirmed cracks as `CREDENTIAL_CRACKED` events (T1110.004).

- Engineered a C2 beacon simulator that mimics APT tradecraft: variable jitter intervals (10–30 seconds), a 90/10 split between small heartbeats (200–500 bytes) and large exfiltration bursts (50 KB–5 MB), and association with real-world APT IP IOCs (APT29, APT41, Lazarus Group) for correlation exercises.

- Constructed an intentionally vulnerable target environment featuring a Flask application with a raw SQL injection vulnerability in the authentication path, a ground station with hardcoded credentials and a predictable JWT secret, and an SMB/LDAP simulation layer generating realistic authentication failure events.

---

### Defensive Security & Detection Engineering

- Designed and implemented a "Deception-as-Code" high-interaction SSH honeypot using Paramiko. The honeypot accepts all credentials unconditionally, presents a convincing interactive shell with fake filesystem responses, and captures every credential pair and issued command as structured events — feeding both the event log and the offline cracking pipeline.

- Built a multi-layer detection stack composing five independent blue team services: a rule-based SIEM correlating exploit and auth-failure events by source IP, a Suricata ET Open signature simulator (Log4j, Cobalt Strike, Nmap), an EDR agent detecting PowerShell encoding flags and LSASS access patterns, a network flow analyzer with exfiltration thresholds, and an automated forensic case generator.

- Implemented automated SOC triage: the network forensics service monitors the event stream for `THREAT_DETECTED` alerts, collects correlated evidence (same IP, same time window), and publishes structured `FORENSIC_CASE` events containing a pre-compiled investigation timeline — reducing analyst workload at the point of detection.

---

### GRC and Compliance Automation

- Built a compliance mapping engine that tags alert events against specific clauses in GDPR (Article 33), NIST (IR-6, CP-2), and the CFAA (18 U.S.C. § 1030), and an automated incident reporting service that generates CISO-addressed incident reports from the event stream — demonstrating integrated GRC automation within a security operations platform.

---

### Frontend and Visualization

- Built a multi-page Next.js 14 dashboard polling the event API at 2-second intervals across domain-specific views (Space, Red Team, Blue Team, Fusion Center). Implemented the space page with satellite list, country filtering, strategic analysis panel (DEFCON, escalation score, war alerts), and real-time event log.

- Integrated Cesium.js (via the Resium React library) for 3D orbital visualization, managing the full Cesium viewer lifecycle within a React component: custom imagery provider, country-coded satellite entities, click-to-select with async orbit path fetch and polyline rendering, and live entity updates on each polling cycle.

---

### DevOps & Infrastructure

- Designed a multi-profile Docker Compose topology for 26+ containers with eight named deployment profiles (`core`, `space`, `red`, `blue`, `target`, `intel`, `grc`, `full`). Profiles share a common infrastructure base and allow independent deployment of any domain subset, with memory limits tuned per service to prevent swap thrashing on development hardware.

- Authored incremental Docker lifecycle scripts (`inc_cycle.sh`, `inc_space.sh`) that build, start, and stream logs while pruning only dangling images (not all stopped containers), preserving layer caches to minimize rebuild times and prevent disk exhaustion during iterative development.

---

## Skills Matrix

### Languages and Frameworks

| Skill | Demonstrated By |
|-------|----------------|
| Python 3.11 | All backend services |
| FastAPI + asyncio | Core API, all Python microservices |
| asyncpg (async PostgreSQL) | Core API database layer |
| Pydantic (schema validation) | Universal event schema enforcement |
| scikit-learn | Satellite country attribution classifier |
| Skyfield (SGP4) | Orbit propagation engine |
| Paramiko | SSH honeypot implementation |
| React / Next.js 14 | Dashboard frontend |
| Cesium.js / Resium | 3D orbital visualization |

### Infrastructure and Data

| Skill | Demonstrated By |
|-------|----------------|
| Docker / Docker Compose | 26+ container orchestration with profiles |
| PostgreSQL 15 (JSONB) | Event lake with schema-less payload storage |
| Redis 7 | Pub/sub event bus and orbit path caching |
| SQL (async queries) | Game state aggregation, event filtering |

### Security Domains

| Domain | Demonstrated By |
|--------|----------------|
| Threat modeling | MITRE ATT&CK coverage across 10 techniques |
| Offensive security | 7 automated red team services |
| Defensive engineering | 6 blue team services with detection pipeline |
| Honeypot design | Paramiko deception SSH shell |
| SIEM / detection engineering | Rule correlation, forensic case automation |
| Intentional vulnerability design | SQL injection, JWT weaknesses, hardcoded secrets |
| GRC / compliance | GDPR, NIST, CFAA mapping automation |

### Space Domain

| Skill | Demonstrated By |
|-------|----------------|
| Orbital mechanics (TLE, SGP4) | Skyfield-based orbit propagation engine |
| Satellite threat assessment | Six-module Space War Detector |
| Space domain awareness | DEFCON fusion from orbital + cyber signals |
| RF signal modeling | SDR simulation service |
| Ground station operations | Vulnerable ground station with auth logging |
| Country attribution via ML | RandomForest on live orbital parameters |

---

## Project Statistics

| Metric | Value |
|--------|-------|
| Total microservices | 26+ |
| Operational domains | 7 (Core, Space, Red, Blue, Target, GRC, Intel) |
| MITRE ATT&CK techniques | 10 |
| Blue team detection layers | 5 independent services |
| Event types in schema | 16 |
| Docker Compose profiles | 8 |
| Orbit path points per computation | 45 (90 min @ 2-min intervals) |
| Space War Detector modules | 6 |
| Frontend polling interval | 2 seconds |
