# Historical Archive: The "NebulaX" Era
### ***This document is related to the 3rd agent's work on this project @conversation: Building Password Auditor Module*** *Some of the information in this document may be outdated, this version does not include the wargame aspect like agent3_with-wargames,md* 
**Timeline:** Project Inception $\rightarrow$ Pre-Wargame Architecture
## 1. The Origin: "NebulaX" Prototype
**Concept:** A lightweight, automated vulnerability scanner and reporting dashboard.
*   **Goal:** To build a system that could scan a target, identify open ports or weak credentials, and visualize the results.
*   **Architecture:**
    *   A simple Python script (`scanner.py`) running `nmap` or basic socket checks.
    *   A basic frontend (likely simple HTML/JS or early React) to list findings.
*   **Vibe:** Functional, utilitarian, "Script Kiddie" toolset.
## 2. The Expansion: "System of Systems"
**Evolution:** The project grew from a single tool into a **Microservices Architecture**.
*   **The "11 Services" Sprint:** We moved from a monolithic script to a distributed system with 11 distinct microservices.
    *   **Core:** Centralized API for data ingestion.
    *   **Red Team:** Split into `attack-engine`, `password-auditor`, and `vuln-scanner`.
    *   **Blue Team:** Split into `ids-suricata`, `honeypot-ssh`, and `detection-engine`.
    *   **Target:** A `public-web` container to serve as the victim.
*   **The "Hybrid" Workflow:** This is where the **Disk Space Constraint** first appeared. We realized we couldn't run 11 Docker containers simultaneously on the host.
    *   **Solution:** We invented the "Hybrid" workflow—running stateful infra (Postgres/Redis) in Docker, but running the 11 service scripts *natively* on the Mac to save resources.
## 3. The Convergence: "OrbitGuard"
**Evolution:** We added a new dimension—**Space**.
*   **Concept:** Cybersecurity doesn't just happen on servers; it happens in orbit.
*   **Feature:** We built the **Space Tracker** service.
    *   It pulled real TLE (Two-Line Element) data from CelesTrak.
    *   It calculated satellite positions (Azimuth/Elevation) relative to a ground station.
    *   It predicted "Next Pass" times.
*   **Result:** The project was renamed/referred to as **NebulaX / OrbitGuard**. It was now a "Cyber-Physical" monitor.
## 4. The Pre-Wargame State (The "Unified Monitor")
**Just before the "Astra Dynamics" pivot, the system was a "Unified Security Monitor".**
### Functionality
*   **Data Ingestion:** The Core API was receiving streams of data:
    *   SSH brute force attempts from the Red Team.
    *   "Threat Detected" alerts from the Blue Team.
    *   Satellite coordinates from Space Guard.
*   **The Dashboard:** A single-page "Glass Pane" view.
    *   It showed *everything* at once: a map, a list of logs, and some basic charts.
    *   There were no "Teams" or "Personas." Everyone saw the same data.
    *   There was no "Score" or "DEFCON." It was purely informational—a dashboard for observing, not playing.
### The Missing Piece
While technically impressive, it lacked **Narrative**.
*   It was just a list of logs.
*   There was no sense of *conflict*. You couldn't tell if the Red Team was "winning" or if the Blue Team was holding the line.
*   **This realization led directly to the "Astra Dynamics" Wargame evolution:** The decision to split the view into Red vs. Blue and add the "Momentum Engine" to gamify the data.
***
**Summary for the Next Engineer:**
"We started with a scanner, exploded it into a microservices cloud, added satellite tracking, and built a unified dashboard. We then realized 'monitoring' is boring, so we pivoted to 'wargaming' to make the data tell a story of conflict."