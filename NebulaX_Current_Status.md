# NebulaX System Status
**Last Updated:** December 6, 2025
**Phase:** 4 - Refinement & Realism

## 1. Executive Summary
The system is currently in a **Functional Prototype** state. The Core Event Bus is stable, and the "Fusion Center" dashboard successfully visualizes data from Space, Red, and Blue teams. We are transitioning from a "Gamified" proof-of-concept to a "Realistic" Cyber-Physical Range.

## 2. Module Health & Hierarchy
*Status Legend:*
*   🟢 **Active:** Fully functional and integrated.
*   🟡 **Partial:** Running, but has known issues or limited scope.
*   🟠 **Simulation:** Placeholder script generating random data.
*   ⚪ **Planned:** Directory exists, but empty/unimplemented.

### 🏛️ Core Infrastructure
*   **`services/core`** (🟢 Active)
    *   **Event Bus:** Redis Pub/Sub operational.
    *   **API:** FastAPI handling ingestion/retrieval.
    *   **Database:** PostgreSQL storing `UniversalEvent` history.
*   **`services/dashboard`** (🟢 Active)
    *   **Fusion Center:** Live. Log filtering implemented (Step 5).
    *   **Space Command:** Upgraded to **CesiumJS 3D Globe** with TLE propagation and orbit trails.
    *   **Team Views:** Red/Blue/Space specific views active.

### 🛰️ Space Guard (OrbitGuard)
*   **`services/space-guard`** (🟢 Active)
    *   **`tracker`:** Fully integrated with **Space-Track.org API** and **Space War Detector**.
        *   **Metadata Fusion:** Fetches authoritative RCS, Launch Year, Country.
        *   **War Detector (Escalation Engine):**
            *   **Maneuver:** Monitors Delta-V/Orbital changes.
            *   **Proximity:** Detects interceptors (<50km).
            *   **Debris:** Monitors catalog growth (ASAT/Collision).
            *   **GNSS:** Jamming/Spoofing detection (Simulated).
            *   **Launch:** Surge events.
            *   **GEO Sentinel:** Drift monitoring.
            *   **Fusion:** Aggregates signals into DEFCON score.
        *   **ML Integration:** Random Forest trained dynamically on Ground Truth data.
    *   **`ground-sim`:** Simulates ground station rotation.
    *   **`rf-receiver`:** RTL-SDR integration (Simulated if no hardware).
    *   **`rf_processor`:** Signal analysis (Placeholder).

### ⚔️ Red Team (Adversary Emulation)
*   **`services/red-team`** (🟡 Partial)
    *   **`attack-engine`:** Hybrid Web/SSH attacker. *Note: Needs more attack vectors.*
    *   **`password-auditor`:** Cracks hashes from the honeypot.
    *   **`vuln-scanner`:** Basic port scanner simulation.
    *   **`web-injector`:** SQLi/XSS automation.
    *   **`c2-beacon`:** Simulates malware callbacks.
    *   **`ransomware-sim`:** Crypto-locker simulation.
    *   **`apt-emulator`:** Advanced Persistent Threat persona (State Actor).

### 🛡️ Blue Team (Security Operations)
*   **`services/blue-team`** (🟡 Partial)
    *   **`honeypot-ssh`:** High-interaction Paramiko trap.
    *   **`blue-sentinel`:** SIEM detection engine.
    *   **`ids-suricata`:** Network intrusion detection.
    *   **`net-watchdog`:** Traffic flow monitor.
    *   **`network-forensics`:** PCAP analysis.
    *   **`edr-agent`:** Endpoint monitoring.
    *   **`detection-engine`:** Correlation logic.

### 🎯 Target Environment
*   **`services/target`** (🟡 Partial)
    *   **`public-web`:** Vulnerable Flask App (SQLi target).
    *   **`internal-infra`:** File server simulation.
    *   **`identity-manager`:** User/Group management simulation.

### 🧠 Intelligence & GRC
*   **`services/intel`** (🟠 Simulation)
    *   **`cve-feeder`:** Randomly injects CVE data.
    *   **`ioc-manager`:** Manages "Known Bad" indicators.
*   **`services/grc`** (🟠 Simulation)
    *   **`incident-reporter`:** Generates PDF reports.
    *   **`policy-mapper`:** Maps alerts to compliance frameworks.

### 🤖 AI Engine
*   **`services/ai-engine`** (⚪ Planned)
    *   **`soc_analyst`:** LLM-based alert triage.
    *   **`scenario_gen`:** Dynamic attack scenario generation.

## 3. History & Trajectory
### Past (Origins)
*   Started as a simple Vulnerability Scanner.
*   Evolved into "NebulaX" (Microservices).
*   Added "OrbitGuard" (Space Tracking).
*   Pivoted to "Astra Dynamics Wargame" (Gamified).

### Present (Current State)
*   **Architecture:** Fully Dockerized (`test_cycle.sh`). Hybrid workflow deprecated.
*   **Focus:** Removing "Game" elements (Score, DEFCON) in favor of "Realism" (Telemetry, Intel).
*   **Issue:** Fusion Center logs were flooding; fixed by splitting streams.

### Future (Roadmap)
*   **Near Term:**
    *   UI Overhaul
    *   Verify all submodules (Red/Blue) are actually generating valid events.
    *   Remidy lag/computational load
*   **Long Term:**
    *   **AI Integration:** Implement `ai-engine` for automated SOC analysis.
    *   **Hardware:** Real RF decoding with RTL-SDR.
    *   **Target Expansion:** Full Active Directory simulation.
    *   **Space-Track Deep Dive:** Expand API usage to include Conjunction Data Messages (CDM) and Decay predictions.

## 4. Known Issues
*   **Submodule Verification:** Many Red/Blue submodules exist but haven't been rigorously tested in the new Docker environment.
*   **Dashboard Graphs:** Needs redesign 