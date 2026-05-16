# NebulaX // OrbitGuard

**A cyber-physical fusion range.** Live NORAD satellite telemetry + automated adversary emulation + a single dashboard that correlates the two.

About 27 Docker microservices around a FastAPI event bus, a Next.js + Cesium dashboard, and an ML-powered satellite-attribution pipeline.

## Get started

```bash
./dev.sh                    # hybrid dev (backend in Docker, dashboard on host) — recommended
docker compose --profile minimal up     # 6-container "just show me satellites" demo
docker compose --profile full up        # all ~27 containers
```

→ Then open <http://localhost:3000/space>

For a full setup walkthrough see [docs/QUICKSTART.md](docs/QUICKSTART.md). For the daily dev recipes (profiles, env vars, troubleshooting), see [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).

## Documentation

This repo has a **documentation system** at [`docs/`](docs/), not a doc pile. Start here:

| If you want to know… | Read |
|---|---|
| What this project is | [docs/PROJECT.md](docs/PROJECT.md) |
| Where things are right now | [docs/STATUS.md](docs/STATUS.md) |
| Where it's going | [docs/ROADMAP.md](docs/ROADMAP.md) |
| What every folder/file does | [docs/PROJECT_MAP.md](docs/PROJECT_MAP.md) |
| The space-domain centerpiece | [docs/ORBITGUARD.md](docs/ORBITGUARD.md) |
| The system architecture and event schema | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| What every service does | [docs/SERVICES.md](docs/SERVICES.md) |

The full docs index lives at [docs/README.md](docs/README.md). Recent changes are in [CHANGELOG.md](CHANGELOG.md).

## What's in it

- **OrbitGuard** — live NORAD TLEs → Skyfield SGP4 propagation → ML country attribution → six-module Space War Detector → 3D Cesium globe with click-to-orbit polylines. The technical centerpiece. See [docs/ORBITGUARD.md](docs/ORBITGUARD.md).
- **Red team** — 7 services emulating SSH brute-force, SQLi, payload delivery, ransomware, C2 beaconing, credential cracking, network recon.
- **Blue team** — 6 services: SSH honeypot (real Paramiko listener), rule-based SIEM, IDS/EDR simulators, network forensics.
- **Target environment** — intentionally vulnerable Flask app + simulated identity/SMB services.
- **Fusion Center** — Next.js dashboard correlating space + cyber telemetry on a single pane.

## Legal

For authorized security research, education, and training in isolated lab environments only. The vulnerable services are simulated targets — never deploy against production systems. All simulated within Docker's bridge network; no real external network connections are made.
