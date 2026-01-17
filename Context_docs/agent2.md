# NebulaX-OrbitGuard: System Handoff & Context 
### ***This document is related to the 2nd agent's work on this project @conversation: System Expansion and Debugging*** *Some of the information in this document may be outdated* 
## 1. General Overview
**NebulaX-OrbitGuard** is a high-fidelity, converged cyber-physical simulation platform. It integrates **Cybersecurity** (Red/Blue/Purple teaming), **Space Operations** (Satellite tracking/RF), and **GRC** (Governance, Risk, Compliance) into a single, unified ecosystem.
The system is designed to simulate a "living" network under constant siege, visualizing complex attack chains, defensive countermeasures, and orbital mechanics in real-time. It is built as a microservices architecture where independent agents (Python) interact with a central nervous system (Core API) to generate a rich, visual data tapestry on a premium Next.js dashboard.
## 2. Specific Overview
### 2a. Functionality
*   **The Core:** A FastAPI backend (`core-api`) backed by PostgreSQL (`nebulax-db`) acts as the central event bus. It ingests, validates, and persists all system activity.
*   **The Agents (Modules):** ~20 specialized Python microservices that simulate specific roles. They generate traffic, attacks, and telemetry.
    *   **Red Team:** Simulates adversaries (Ransomware, C2 Beacons, SQLi, APT campaigns).
    *   **Blue Team:** Simulates defense (Suricata IDS, EDR agents, Honeypots, Forensics).
    *   **Space Guard:** Tracks satellites (TLE data) and simulates RF signal interception.
    *   **Target:** Simulates victim infrastructure (Web apps, Internal AD, File shares).
    *   **Intel & GRC:** Feeds threat intelligence and maps events to legal frameworks (GDPR/NIST).
*   **The Dashboard:** A "Movie-OS" style interface (Next.js, Tailwind, Recharts, Leaflet) that polls the Core to visualize attacks, satellite positions, and network flows in a high-tech, dark-mode UI.
### 2b. Operations (The "Hybrid Workflow")
**CRITICAL:** This project operates on a **Hybrid Workflow** due to hardware constraints.
*   **Docker:** Runs the `core-api`, `database`, and the lightweight Python agents (using Alpine Linux).
*   **Localhost:** Runs the `dashboard` (via `npm run dev`) and occasionally agents during debugging.
*   **Networking:**
    *   Services use the `CORE_HOST` environment variable.
    *   In Docker, `CORE_HOST=nebulax-core`.
    *   Locally, `CORE_HOST=localhost`.
    *   The Dashboard connects to `localhost:8000` (Core) via `NEXT_PUBLIC_API_HOST`.
### 2c. Constraints & Guardrails
*   **Storage is Critical:** The host machine (MacBook Air) has very limited disk space (~8GB free).
    *   **Rule:** ALWAYS use `python:3.10-alpine` for Python containers (50MB vs 125MB).
    *   **Rule:** NEVER build the Dashboard in Docker unless absolutely necessary (it creates massive images). Run it locally.
    *   **Rule:** Aggressively prune Docker artifacts (`docker system prune`) if builds fail.
*   **Schema Strictness:** The Core API enforces a strict `UniversalEvent` schema (Pydantic).
    *   Events must be nested: `{ "event_meta": {...}, "context": {...}, "payload": {...} }`.
    *   Flat JSON payloads will be rejected with `422 Unprocessable Entity`.
*   **Simulation vs. Reality:** While the architecture is real, the *attacks* are currently simulated (e.g., `requests.post` with a payload description) rather than actual binary exploitation, to maintain safety and control.
## 3. Roadmap: How We Got Here
1.  **Inception:** Started with basic Red/Blue/Space modules and a simple dashboard.
2.  **The "Black Hole" Bug:** Fixed a critical issue where C2 beacons weren't appearing due to Docker networking mismatches (`localhost` vs `host.docker.internal`).
3.  **Hybrid Refactor:** Rewrote all service connection logic to support the Hybrid Workflow, allowing flexible development without massive Docker builds.
4.  **Systematic Expansion:** Recently scaled from ~6 to **20+ modules** in a single sprint, covering GRC, Intel, and advanced Red/Blue tactics.
5.  **Optimization:** Switched all new modules to Alpine Linux to fit the entire fleet into the limited storage space.
6.  **Schema Unification:** Patched all 20 modules to adhere to the `UniversalEvent` schema, ensuring data consistency.
## 4. Core Desires & Philosophy
*   **"Wow" Factor:** The user prioritizes aesthetics. The system should *look* like it belongs in a sci-fi movie or a top-tier SOC. Visuals (animations, glassmorphism, maps) are as important as the backend logic.
*   **Complexity Management:** The user wants a complex system but needs it to be manageable. The modular design allows adding new "capabilities" (modules) without breaking the core.
*   **Educational/Portfolio Value:** This is a resume-defining project. It demonstrates mastery of Microservices, Docker, React, Python, and Cybersecurity concepts.
## 5. Future Enhancement Plans
*   **True Interaction:** Move from "simulated" events to "actual" traffic. (e.g., The `web-injector` actually sending HTTP requests that the `ids-suricata` container intercepts and logs).
*   **Hardware Integration:** Connect a real RTL-SDR dongle to the `rf-receiver` module to ingest *real* radio signals into the dashboard.
*   **AI Analysis:** Implement an LLM-based "Purple Team" analyst that reads the event stream and suggests remediation strategies in real-time.
*   **PDF Reporting:** Upgrade `incident-reporter` to generate actual downloadable PDF reports for GRC compliance.
## 6. User Desires (For the Agent)
*   **Be Proactive but Safe:** Fix small things automatically, but ask before big destructive actions (like wiping Docker).
*   **Context Aware:** Remember the storage limit. Don't suggest "just install this massive library" without checking overhead.
*   **Visual Thinker:** When discussing the dashboard, think about how data *looks*. Suggest charts, colors, and layouts that enhance the "cyber-warfare" aesthetic.
*   **No "Toy" Code:** Even though it's a simulation, write production-grade code (proper error handling, environment variables, modular structure).
## 7. Engineer-to-Engineer Notes
*   **The "Dashboard" Service in Docker is commented out** in `docker-compose.yml`. This is intentional to save space. Do not uncomment it unless the user specifically asks to deploy a production build.
*   **Next.js Binary Corruption:** If the local dashboard fails with `code signature invalid` or SWC errors, run `npm rebuild` inside `services/dashboard`. This happens sometimes after Docker filesystem interactions.
*   **Event Enum:** If you add a new event type, you MUST update the `EventType` Enum in `services/core/schemas.py` first, or the API will reject it.
