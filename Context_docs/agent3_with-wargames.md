# Astra Dynamics Wargame Platform: System Handoff & Context
### ***This document is related to the 3rd agent's work on this project @conversation: Building Password Auditor Module*** *Some of the information in this document may be outdated, this version includes the wargame aspect which I have doubts about* 
**Project Codename:** Astra Dynamics (formerly NebulaX / OrbitGuard)
**System Type:** Multi-Tenant Cyber Warfare Range & Space Defense Simulation
## 1. General Overview
The system is a high-fidelity **Cyber-Physical Wargame** simulating a live conflict between an Advanced Persistent Threat (APT) group known as **"The Syndicate"** (Red Team) and a Defense Contractor known as **"Astra Dynamics"** (Blue Team).
Unlike standard dashboards, this platform is designed as an immersive "movie-style" interface. It visualizes the "Tug of War" between attackers and defenders in real-time, integrating cyber events (exploits, patches) with kinetic space telemetry (satellite orbits, signal jamming).
## 2. Specific Overview
### 2a. Functionality
*   **Multi-Tenancy:** The platform serves four distinct operational personas, each with a dedicated view:
    *   🔴 **Red Team ("The Syndicate"):** Offensive campaign status, exploit logs, and target lists.
    *   🔵 **Blue Team ("Astra SecOps"):** Defense center, IDS alerts, system health, and containment status.
    *   🛰️ **Space Command ("OrbitGuard"):** Real-time satellite telemetry, orbital mapping, and physics data.
    *   🟣 **Fusion Center ("God View"):** Executive oversight combining all data streams into a unified battle timeline.
*   **Game State Engine:** A "Momentum Engine" calculates a live **DEFCON Level (5-1)** and a **Red vs. Blue Score** based on event severity.
*   **Simulated RBAC:** A "Secure Terminal" login system restricts access to specific personas using simulated credentials (e.g., `syndicate` / `hunter2`).
### 2b. Operations (The Hybrid Workflow)
The system runs in a specific **Hybrid Mode** to balance performance with resource constraints:
*   **Infrastructure:** PostgreSQL and Redis run in **Docker** containers.
*   **Applications:** The Core API (FastAPI) and Dashboard (Next.js) run **natively** on the host machine (`localhost`).
*   **Agents:** Python scripts (Red/Blue/Space agents) run natively and communicate via `localhost:8000`.
*   **Controller:** A `wargame_controller.py` script orchestrates the entire simulation loop.
### 2c. Constraints & Guardrails
*   **⚠️ CRITICAL: Disk Space:** The host environment has extremely limited disk space.
    *   **Rule 1:** Do NOT create unnecessary Docker images. Use the Hybrid workflow.
    *   **Rule 2:** When running full system tests, use the "Test & Nuke" strategy (run tests, then aggressively prune all Docker volumes/images).
*   **Visuals First:** The user prioritizes "Wow factor" and aesthetic realism. If the data is simulated, it must *look* real.
*   **Simulation vs. Reality:** Currently, the backend generates synthetic data. The goal is to make the *experience* feel real, even if the underlying hacks are simulated scripts.
## 3. Roadmap & Evolution
*   **Phase 1: Prototype (NebulaX):** Started as a simple vulnerability scanner and dashboard.
*   **Phase 2: Architecture Split:** Separated into Core API and Dashboard services.
*   **Phase 3: The "Wargame" Pivot:** Refactored the system to support the "Red vs. Blue" narrative. Added the "Momentum Engine" for scoring.
*   **Phase 4: Visual Polish:** Implemented the "Astra Dynamics" branding, dark/terminal aesthetics, and the 4-persona split.
*   **Phase 5: Login Simulation:** Added the secure terminal login flow to enhance immersion.
## 4. System Desires (Core Philosophy)
*   **"The Movie Experience":** The interface should feel like a screen from a high-budget sci-fi or spy thriller. It should be dense with data but highly readable.
*   **Gamification:** The conflict must be visible. The "Tug of War" bar and DEFCON levels are central to showing who is winning.
*   **Interactivity:** The system should eventually move from "watching" a simulation to "playing" it (e.g., clicking a button to launch a satellite or block an IP).
## 5. Future Enhancement Plans
*   **Interactive Controls (Path A):**
    *   **Blue Team:** Add buttons to "Block IP," "Isolate Host," or "Deploy Patch."
    *   **Red Team:** Add a "Launchpad" to trigger specific attacks (SQLi, Phishing) on demand.
*   **AI Personas (Path B):** Integrate LLMs to generate realistic chat logs between "Syndicate" hackers and "SecOps" analysts, reacting to the game state in real-time.
*   **Real Infrastructure (Path C):** Eventually replace simulated scripts with real tools (Nmap, Suricata) running against vulnerable containers (DVWA).
## 6. User Desires for the Agent
*   **Be Proactive but Planned:** The user appreciates a solid plan (`implementation_plan.md`) before writing code.
*   **Focus on Visuals:** Don't just make it work; make it look *cool*.
*   **Respect Constraints:** Always be mindful of the disk space limitation. Never bloat the environment.
*   **Roleplay:** Maintain the immersive "Engineer at Astra Dynamics" vibe.
## 7. Engineer-to-Engineer Notes
*   **Credentials:**
    *   Red: `syndicate` / `hunter2`
    *   Blue: `analyst` / `defense`
    *   Space: `operator` / `orbit`
    *   Fusion: `director` / `astra`
*   **Running the Sim:**
    1.  `docker compose up -d postgres redis`
    2.  `npm run dev` (in `services/dashboard`)
    3.  `python3 wargame_controller.py` (in root)
*   **Codebase:** The `services/dashboard` is Next.js/Tailwind. The `services/core` is FastAPI/SQLAlchemy. The agents are pure Python.