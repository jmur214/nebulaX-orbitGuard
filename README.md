# 🌌 NebulaX // Cyber-Physical Fusion Center

> **"Department-in-a-Box" Cyber Range**
> Integrating Orbital Mechanics, Operational Technology, and Enterprise Security.

---

## 🎯 The Mission
**NebulaX** is not just a simulation; it's a **Cyber-Physical Range** designed to demonstrate the convergence of space operations and cybersecurity. It simulates a defense contractor ("Astra Dynamics") under active siege from state-sponsored threats, requiring a unified response across terrestrial and orbital domains.

### Core Capabilities
*   **🛰️ OrbitGuard:** Real-time satellite tracking using NORAD TLE data and SGP4 propagation.
*   **⚔️ Red Team:** Automated adversary emulation (APT29-style) targeting Web, SSH, and OT assets.
*   **🛡️ Blue Team:** "Deception-as-Code" honeypots and a custom SIEM for threat hunting.
*   **🧠 Fusion Center:** A "Single Pane of Glass" correlating physics telemetry with cyber alerts.

---

## 📚 Documentation Suite
We maintain a rigorous documentation standard to ensure the system is "Resume-Ready" at all times.

| Document | Purpose |
| :--- | :--- |
| **[Master Plan](NebulaX_Master_Plan.md)** | The strategic vision and "End State" goals for each pillar. |
| **[System Context](NebulaX_System_Context.md)** | Architectural blueprint, ports, and network topology. |
| **[Current Status](NebulaX_Current_Status.md)** | Live health check of all 20+ microservices. |
| **[Resume Assets](NebulaX_Resume_Assets.md)** | Technical skills and achievements extracted from the codebase. |
| **[Reminders](Reminders.md)** | **The Orchestrator.** Protocols for agents and developers. |

---

## 🏗 Architecture

The system uses a **Event-Driven Microservices Architecture**.

```mermaid
graph TD
    subgraph "Core Infrastructure"
        Bus{Event Bus (Redis)}
        DB[(Data Lake)]
        Dash[Mission Control UI]
    end

    subgraph "Space Domain"
        Space[OrbitGuard Tracker] --> Bus
        Ground[Ground Station Sim] --> Bus
    end

    subgraph "Cyber Domain"
        Honey[SSH Honeypot] --> Bus
        Web[Vulnerable Portal] --> Bus
        RedBot[Attack Engine] --> Web
        Sentinel[Blue Team SIEM] <--> Bus
    end

    Bus --> DB
    DB --> Dash
```

---

## 🚀 Quick Start

**Protocol:** We use a unified script to manage the Docker lifecycle and prevent disk exhaustion.

```bash
# 1. Start the Simulation (Builds, Runs, and Streams Logs)
./test_cycle.sh
```

**Access Points:**
*   **Fusion Center:** `http://localhost:3000`
*   **Core API:** `http://localhost:8000/docs`
*   **Target Portal:** `http://localhost:8080`

**Shutdown:**
*   Press `Ctrl+C`. The script will automatically **prune** all Docker artifacts.
