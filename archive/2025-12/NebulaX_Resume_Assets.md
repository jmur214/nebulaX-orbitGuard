# NebulaX Resume Assets
**Project:** NebulaX Fusion Center + OrbitGuard
**Role:** Senior Cybersecurity Architect & Space Systems Engineer

## 🚀 Technical Achievements

### 1. Cyber-Physical Convergence (Space Systems)
*   **"Engineered a real-time Orbital Dynamics Engine (`space.tracker`) using Python and `Skyfield`. Implemented SGP4 propagation models to calculate satellite look-angles and ground-track coordinates from NORAD TLE data."**
*   **"Designed a 'Fusion Center' dashboard that correlates orbital telemetry with terrestrial cyber threats, providing a unified Common Operating Picture (COP) for multi-domain operations."**
*   **"Simulated Ground Station operations (`space.ground-sim`) to model the physical rotation of antennas based on predicted satellite passes."**
*   **"Developed a high-fidelity 3D Common Operating Picture (COP) using `CesiumJS` and `React`, implementing client-side SGP4 propagation (via `satellite.js`) to render 1000+ orbital objects with real-time day/night physics and predictive orbit trails."**
*   **"Architected a 'Space War Escalation Detector' that fuses 7 independent signal streams into a real-time DEFCON risk score:"**
    *   **"Maneuver Detection Engine:"** Analyzes TLE history to calculate delta-v ($\Delta v$) and orbital element changes (Semimajor Axis, Inclination, Eccentricity). Identifies orbit-raising events and plane-change maneuvers indicative of rendezvous intent.
    *   **"Proximity & RPO Monitor:"** Implements an $O(N^2)$ Euclidean distance check to detect "Inspector Satellites" performing Rendezvous and Proximity Operations (RPO). Flags high-risk intercepts (<50km) and co-orbital stalking behaviors.
    *   **"Debris Event Listener:"** Monitors the satellite catalog for sudden spikes in object density, detecting potential Anti-Satellite (ASAT) weapon tests or kinetic collisions.
    *   **"GNSS Interference Sentinel:"** Simulates the detection of GPS/GLONASS jamming signals by correlating terrestrial interference reports with satellite ground tracks.
    *   **"Launch Activity Monitor:"** Analyzes launch cadence data to detect "Surge" events—rapid, unannounced launch campaigns often preceding conflict.
    *   **"GEO Belt Sentinel:"** Specifically monitors the Geostationary Belt for "Slot Drift" and unauthorized repositioning of strategic communication assets.
    *   **"Behavioral Fusion Classifier:"** Aggregates these disparate signals into a weighted Risk Index (0-100) and maps it to a DEFCON level, minimizing false positives through multi-factor correlation.

### 2. Offensive Security Engineering (Red Team)
*   **"Developed a polymorphic 'Attack-as-Code' engine (`red.attack-engine`) capable of executing automated kill-chains against simulated infrastructure."**
*   **"Implemented a custom Command & Control (C2) beacon (`red.c2-beacon`) that mimics advanced malware heartbeat patterns to test defensive sensor coverage."**
*   **"Built an automated Credential Auditor (`red.password-auditor`) that intercepts authentication attempts and performs offline hash cracking against a breach database."**

### 3. Defensive Engineering & SIEM (Blue Team)
*   **"Architected a 'Deception-as-Code' High-Interaction Honeypot (`blue.honeypot-ssh`) using `Paramiko`. Successfully captured adversary keystrokes and TTPs for forensic analysis."**
*   **"Deployed a custom SIEM engine (`blue.sentinel`) that ingests heterogenous log sources (Suricata, Syslog, App Logs) and applies correlation logic to detect complex threats."**
*   **"Integrated Network Forensics capabilities (`blue.network-forensics`) to analyze PCAP data and reconstruct attack flows."**

### 4. DevSecOps & Cloud Architecture
*   **"Designed a scalable, Event-Driven Microservices Architecture using Docker Compose and Redis Pub/Sub. Orchestrated 20+ specialized containers including Databases, APIs, and Simulation Agents."**
*   **"Enforced a strict 'Universal Event Schema' using Pydantic to ensure data consistency and type safety across a polyglot environment (Python/Node.js)."**
*   **"Optimized the CI/CD lifecycle with a custom orchestration script (`test_cycle.sh`) that handles build automation, log streaming, and aggressive Docker resource pruning."**

## 🛠 Skills Matrix
*   **Languages:** Python (FastAPI, Skyfield, Paramiko, SQLAlchemy), JavaScript/TypeScript (React, Next.js).
*   **Infrastructure:** Docker, Docker Compose, PostgreSQL, Redis.
*   **Security:** SIEM Design, Honeypots, Red Teaming, OWASP Top 10, Cryptography, Network Forensics.
*   **Space Domain:** Orbital Mechanics (TLE, SGP4), Ground Station Operations, RF Signal Analysis.
