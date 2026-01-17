# PROJECT: NEBULAX FUSION CENTER + ORBITGUARD
**Role:** Senior Cybersecurity Architect & Space Systems Engineer
**Goal:** A "Department-in-a-Box" Cyber-Physical System simulating the defense of terrestrial and orbital assets.

## 1. High-Level Architecture
* **The Core (NebulaX):** A modular SIEM/SOAR platform acting as the central nervous system.
* **The Plugin (OrbitGuard):** A specialized "Critical Infrastructure" vertical focusing on Space Domain Awareness (SDA).
* **The Pattern:** Event-Driven Microservices (Python/Node) communicating via a Central Event Bus (JSON) to a Data Lake (PostgreSQL).

## 2. The 5 Strategic Pillars

### I. The Battlefield (Target Environment)
* **Simulated Entity:** "Astra Dynamics" (Defense Contractor).
* **`target.public.web`:** Corporate portal with intentional OWASP flaws (SQLi, XSS).
* **`target.internal.infra`:** Internal file servers and AD simulations.
* **`target.identity.manager`:** Generates fake employee personas and PII.

### II. Blue Team (Security Operations)
* **`blue.honeypot.ssh`:** High-interaction trap logging keystrokes and TTPs.
* **`blue.net.watchdog`:** Network flow analyzer (NetFlow/IPFIX).
* **`blue.network.forensics`:** Deep Packet Inspection (PCAP/Zeek).
* **`blue.ids.suricata`:** Signature-based detection (ET Open rules).
* **`blue.edr.agent`:** Endpoint detection (kernel hooks).
* **`blue.ueba.engine`:** Behavioral analytics (ML-based anomaly detection).

### III. Red Team (Adversary Emulation)
* **`red.password.auditor`:** Credential stuffing and hash cracking.
* **`red.vuln.scanner`:** Automated CVE scanning (Nmap/Nessus style).
* **`red.c2.beacon`:** Low-and-slow malware implant simulation.
* **`red.web.injector`:** Automated SQLi/XSS attacks.
* **`red.apt.emulator`:** State-actor persona engine (e.g., APT29 tactics).
* **`red.ransomware.sim`:** Safe crypto-locker simulation.

### IV. Fusion Layer (Intel & GRC)
* **`grc.policy.mapper`:** Maps technical alerts to legal frameworks (CFAA, GDPR, Space Law).
* **`grc.incident.reporter`:** Automated PDF generation for C-Suite/Legal.
* **`intel.cve.feeder`:** Real-time vulnerability ingestion.
* **`intel.ioc.manager`:** "Known Bad" IP/Hash management.

### V. OrbitGuard (Space Vertical)
* **`space.tracker`:** Orbital mechanics engine (Skyfield) & TLE propagation.
* **`space.ground.sim`:** Vulnerable OT/Ground Station interface.
* **`space.rf.receiver`:** Hardware integration (RTL-SDR) for signal capture.
* **`space.hardware.bridge`:** Physical rotator control (Raspberry Pi).

## 3. Technology Stack
* **Backend:** Python (FastAPI/Flask)
* **Frontend:** Next.js + React + Leaflet (Tactical 2D Maps)
* **Data:** PostgreSQL (JSONB), Redis (Pub/Sub)
* **Infra:** Docker & Docker Compose