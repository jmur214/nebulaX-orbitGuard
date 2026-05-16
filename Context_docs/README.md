> **⚠ FROZEN SNAPSHOT — DO NOT EDIT.**
>
> This directory is a deliberately frozen Dec 5, 2025 snapshot used for AI-agent
> context-loading. The content below reflects the project as of that date and is
> intentionally NOT kept in sync with reality.
>
> For current documentation see [`../docs/`](../docs/). For current status see
> [`../docs/STATUS.md`](../docs/STATUS.md). For the project map see
> [`../docs/PROJECT_MAP.md`](../docs/PROJECT_MAP.md).

---

Readme 
# 🌌 NebulaX // Cyber-Physical Fusion Center

**NebulaX** is a distributed "Department-in-a-Box" Cyber Range that integrates **Orbital Mechanics**, **Operational Technology (OT)**, and **Enterprise Security**.

It is designed to simulate a complete cyber-warfare ecosystem:

1.  **OrbitGuard (Space):** Tracks real-world satellites and predicts acquisition windows.
2.  **Red Team (Offense):** Automates adversary emulation (SQLi, Brute Force, C2 Beaconing).
3.  **Blue Team (Defense):** Runs a custom SIEM (Sentinel) and Deception Grid (Honeypots).
4.  **Core (Fusion):** Aggregates physics telemetry and cyber threats into a single "Mission Control" dashboard.

---

## 🏗 Architecture

The system uses a **Hub-and-Spoke** microservices architecture. All modules communicate via a centralized Event Bus (FastAPI/Redis) using a strict JSON schema.

```mermaid
graph TD
    subgraph "Core Infrastructure"
        Bus{Event Bus}
        DB[(Data Lake)]
        Dash[Mission Control UI]
    end

    subgraph "Sensors & Targets"
        Space[OrbitGuard Physics] --> Bus
        Honey[SSH Honeypot] --> Bus
        Web[Vulnerable Portal] --> Bus
    end

    subgraph "Adversary Emulation"
        RedBot[Attack Engine] --> Web
        Cracker[Password Auditor] <--> Bus
        Scanner[Vuln Scanner] --> Bus
    end

    subgraph "Active Defense"
        Sentinel[Blue Team SIEM] <--> Bus
    end

    Bus --> DB
    DB --> Dash
```

---

## 🚀 Getting Started (Hybrid Workflow)

Due to the resource intensity of running 12+ containers, we use a Hybrid Workflow:
* **Docker:** Runs Infrastructure (Postgres, Redis).
* **Host (Mac/Linux):** Runs Application Logic (Python, Node) natively.

### Prerequisites
* Docker Desktop
* Python 3.10+
* Node.js 18+

### 1. Start Infrastructure
Boot the Database and Event Bus.

```bash
docker compose up -d
```

### 2. Start the "Brain" (Core API)
*Terminal Tab A*

```bash
cd services/core
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Point to local Docker DB
export DATABASE_URL="postgresql+asyncpg://admin:nebulax_secret@localhost:5432/nebulax_core"

uvicorn main:app --reload --port 8000
```

### 3. Start the "Face" (Dashboard)
*Terminal Tab B*

```bash
cd services/dashboard
npm install
npm run dev
# Access at http://localhost:3000
```

---

## 🎮 Simulation Playbook (How to Hack NebulaX)

The following scenarios demonstrate the "Closed Loop" nature of the range.

### Scenario A: The SQL Injection (Web)
* **Target:** `target.public.web` (Port 8080)
* **Goal:** Bypass authentication to steal "Project Orion" blueprints.

**Start the Target:**
```bash
cd services/target/public-web
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
python app.py
```

**The Attack:**
1.  Open browser to `http://localhost:8080`.
2.  Username: `admin' --`
3.  Password: (Leave Blank)
4.  Click Authenticate.

**The Result:** You will bypass the login logic.
**The Evidence:** Check the Dashboard. You will see `WEB_TRAFFIC` logs showing the malicious query.

### Scenario B: The Honey-Trap (Identity)
* **Target:** `blue.honeypot.ssh` (Port 2222)
* **Goal:** Capture attacker credentials and crack them.

**Start the Trap:**
```bash
cd services/blue-team/honeypot-ssh
# (Install dependencies...)
python main.py
```

**Start the Hunter (Red Team):**
*(In a separate tab)*
```bash
cd services/red-team/password-auditor
# (Install dependencies...)
python main.py
```

**The Attack (Manual):**
Open a new terminal and SSH into the trap:
```bash
ssh -p 2222 admin@localhost
```
Enter a weak password (e.g., `password123`).

**The Result:** You will enter the fake shell (`admin@astra:~$`). Run commands like `ls` or `whoami`.
**The Evidence:** Dashboard: You will see `AUTH_FAILURE` followed by a **HIGH Severity** `CREDENTIAL_CRACKED` alert (because the Auditor caught you using a weak password).

### Scenario C: Space Domain Awareness
* **Goal:** Visualize orbital assets.

**Start the Physics Engine:**
```bash
cd services/space-guard/tracker
# (Install dependencies...)
python main.py
```

**The Result:**
* The Dashboard will display the live Azimuth/Elevation of NOAA-20.
* The 2D Map will plot the satellite's Ground Track relative to your station.
* The "Next Acquisition" timer will countdown to the next pass.

---

## 📦 Module Manifest

| Pillar | Module | Function |
| :--- | :--- | :--- |
| **CORE** | `core.events` | Central API Gateway & Event Bus. |
| **SPACE** | `space.tracker` | Calculates orbital paths using NORAD TLE data. |
| **TARGET** | `target.public.web` | Vulnerable Flask App (SQLi/XSS target). |
| **BLUE** | `blue.honeypot.ssh` | High-interaction trap; logs keystrokes. |
| **BLUE** | `blue.sentinel` | SIEM detection engine; fires alerts on threats. |
| **RED** | `red.attack.engine` | Hybrid bot; attacks Web & SSH automatically. |
| **RED** | `red.pass.auditor` | Sniffs logs for weak passwords & cracks them. |
| **RED** | `red.vuln.scanner` | Nmap wrapper; finds open ports. |
| **RED** | `red.c2.beacon` | Simulates malware "heartbeat" traffic. |

---

## 🛠 Troubleshooting

**"Docker storage full / Input Output Error"**
Run the nuke command:
```bash
docker system prune --all --volumes --force
```
If that fails, delete `~/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw`.

**"Python Module Not Found"**
* Ensure you activated the `venv` in that specific folder before running the script.
* Run `pip install -r requirements.txt` again.

**"Dashboard Map is Grey"**
Ensure the `space.tracker` script is running. The map defaults to `[0,0]` until it receives the first GPS coordinate from the physics engine.
