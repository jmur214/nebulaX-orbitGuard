# Project map — every folder, what it is and does

> [← docs index](README.md)

A folder-level catalog (not a file-by-file dump — that rots). Update this when folders are added, renamed, or change purpose. Do not update for routine file edits.

## Top-level layout

```
nebulaX-orbitGuard/
├── README.md             ← Entry point — short, links into docs/
├── CHANGELOG.md          ← Append-only log of notable changes
├── docker-compose.yml    ← All ~27 services + profiles (minimal/core/space/red/blue/...)
├── docker-compose.dev.yml ← Override for hot-reload-in-Docker dashboard
├── dev.sh                ← Canonical dev entry point (hybrid mode)
├── dev_hybrid.sh         ← Legacy alias; calls into same path
├── inc_cycle.sh          ← "Build full stack, run, prune" loop
├── inc_space.sh          ← Same, but for the minimal/space profile
├── docs/                 ← THIS DOCUMENTATION SYSTEM
├── services/             ← All microservices (see below)
├── infrastructure/       ← Shared infra (Python base image, future: postgres/nginx if added)
├── scripts/              ← Helper scripts (build_base.sh, test_module.sh, dev_core.sh)
├── shared/               ← (Empty skeleton; no shared lib code today)
├── archive/              ← Superseded docs from prior phases
├── Context_docs/         ← Frozen Dec 2025 snapshot for AI-agent context-loading
├── internal_notes/       ← Author's working notes (gitignored)
├── tests/                ← (sparse; testing not yet a strong story)
└── venv/                 ← Python virtualenv (gitignored)
```

## services/

### services/core/
**Purpose:** FastAPI event bus, game state, on-demand orbit computation. The single chokepoint every service writes to.
**Key files:**
- `main.py` — endpoints (`/events/ingest`, `/events/recent`, `/game/state`, `/satellite/orbit`); CORS; event retention background task
- `schemas.py` — `UniversalEvent` Pydantic model, `EventType` enum, `EventSeverity` enum
- `db/database.py` — async SQLAlchemy engine, `get_db` dependency, `SQL_ECHO` toggle
- `db/models.py` — single `EventModel` table with JSONB `context` + `payload`
- `orbit_computer.py` — Skyfield SGP4 path generator
- `Dockerfile`, `requirements.txt` — uses `nebulax-python-base`; CMD runs `uvicorn`
**Listens on:** 8000 (host-mapped). **Reads/writes:** PostgreSQL, Redis.
**Empty skeleton dirs inside:** `api/`, `models/` (intended structure never used; real code is flat).

### services/dashboard/
**Purpose:** Next.js 14 + React + Cesium 3D globe + 2D Leaflet map. The Fusion Center.
**Key files:**
- `src/pages/index.js` — mission-select landing
- `src/pages/login.js` — hardcoded-creds gate (`AuthContext.js`)
- `src/pages/space.js` — **OrbitGuard space view** (Cesium globe + Strategic Analysis panel)
- `src/pages/fusion.js` — executive view with 2D map + unified event log
- `src/pages/red.js`, `blue.js` — per-team views
- `src/components/SatelliteGlobe.js` — Cesium Viewer + click handler + orbit polyline
- `src/components/SatelliteMap.js` — Leaflet 2D fallback (used by fusion.js)
- `src/components/EventLog.js`, `AttackChart.js`, `NetworkTrafficChart.js`
- `src/context/AuthContext.js` — hardcoded demo creds (director/operator/analyst/syndicate)
- `next.config.js` — Cesium webpack config, `reactStrictMode: false` (Cesium double-mount races)
- `Dockerfile` — multi-stage production build (post-A3)
- `Dockerfile.dev` — single-stage dev build with `npm run dev` (opt-in via docker-compose.dev.yml)
**Listens on:** 3000.

### services/space-guard/

#### tracker/
**Purpose:** The OrbitGuard centerpiece. Fetches live NORAD TLEs (Space-Track → Celestrak fallback), propagates orbits with Skyfield from a Chicago Topos, trains a `RandomForestClassifier` at startup on inclination + apogee for country attribution, and runs the six-module Space War Detector every 60 s.
**Key files:**
- `main.py` — fetch + ML training + per-satellite telemetry loop
- `war_detector/detector.py` — fuses six submodule outputs into per-sat + global metrics
- `war_detector/submodules/{maneuver,proximity,debris,gnss,launch,geo}.py` — one detector each
- `war_detector/scoring/classifier.py` — escalation score → DEFCON mapping
- `de421.bsp` — planetary ephemeris (required at runtime; do NOT remove from this dir)
- `stations.txt`, `weather.txt` — local fallback TLE data
- `orbital_fingerprint.png` — emitted scatter plot of inclination vs apogee
**Reads:** Space-Track + Celestrak + Launch Library 2. **Writes:** core API.

#### ground-sim/
**Purpose:** Intentionally vulnerable Flask ground-station endpoint.
**Vulnerabilities (deliberate):** hardcoded admin/solarwinds123, hardcoded JWT secret, weak token check (IDOR).
**Listens on:** 5001 (host) → 5000 (container).

#### rf-receiver/
**Purpose:** Simulated RTL-SDR signal capture. Emits random `RF_SIGNAL_CAPTURED` events every 10 s.

#### rf_processor/
**Purpose:** Empty skeleton dir; planned RF signal analysis.

### services/red-team/
Seven adversary-emulation services. **Most are timer-based synthetic event generators**; two make real network calls.

| Folder | What it actually does | Real network? |
|---|---|---|
| `attack-engine/` | SSH brute-force against honeypot:2222 + SQLi against target-web:5000 | ✅ |
| `vuln-scanner/` | `nmap -sV` against honeypot + target-web every 60 s | ✅ (nmap binary baked in) |
| `password-auditor/` | Polls core API for AUTH_FAILUREs, matches against rockyou wordlist, emits CREDENTIAL_CRACKED | Reactive |
| `c2-beacon/` | Synthetic C2 callbacks (hardcoded APT29/41/Lazarus IPs); claims exfil but does nothing | Synthetic |
| `apt-emulator/` | Synthetic kill-chain stage events on a 20 s timer | Synthetic |
| `ransomware-sim/` | Synthetic FILE_ENCRYPTED + RANSOM_NOTE pairs every 20–60 s | Synthetic |
| `web-injector/` | Synthetic WEB_TRAFFIC events with SQLi/XSS/LFI payload strings | Synthetic (code stub never sends) |

**Empty skeleton:** `password_lab/`.

### services/blue-team/
Six defensive services. **One is a real listener** (honeypot-ssh); the rest are API pollers or random-timer generators.

| Folder | What it actually does |
|---|---|
| `honeypot-ssh/` | Real Paramiko SSH listener on 2222, accepts all creds, logs AUTH_FAILURE/SUCCESS/COMMAND_EXECUTED |
| `detection-engine/` (runs as `blue-sentinel` container) | Polls core API every 2 s for EXPLOIT_SUCCESS, emits THREAT_DETECTED |
| `net-watchdog/` | Polls for NETWORK_FLOW > 1MB and VULN_REPORTs, emits alerts |
| `network-forensics/` | Polls for THREAT_DETECTED, generates synthetic FORENSIC_CASE records |
| `ids-suricata/` | 10-second timer, 50% chance to emit a random ET signature alert |
| `edr-agent/` | 15-second timer, 50% chance to emit a random host-based alert |

**Empty skeleton:** `sensor/`.

### services/target/
Intentionally vulnerable target environment.

| Folder | What it is |
|---|---|
| `public-web/` | Flask web portal with SQL injection at `/login` (flag: `flag{astra_master_key_xyz}`) |
| `internal-infra/` | Synthetic SMB-style NETWORK_FLOW emitter |
| `identity-manager/` | Synthetic AUTH_FAILURE emitter with Faker-generated usernames |

### services/intel/

| Folder | What it is |
|---|---|
| `cve-feeder/` | Cycles through 3 hardcoded CVEs (Log4j, openssh-XZ, http/2) as VULN_REPORTs |
| `ioc-manager/` | Synthetic IOC-sync INFO events every 30 s |

### services/grc/

| Folder | What it is |
|---|---|
| `incident-reporter/` | Synthetic RPT-* report events |
| `policy-mapper/` | Synthetic compliance-mapping INFO events (GDPR Art. 33, NIST, CFAA) |

### services/ai-engine/
**Empty skeletons:** `soc_analyst/`, `scenario_gen/`. Planned; see [ROADMAP.md](ROADMAP.md).

## infrastructure/

### python-base/
**Purpose:** The shared base image every Python service `FROM`s.
- `Dockerfile` — `python:3.11-slim-bookworm` + common system packages + common pip set
- `requirements.txt` — the cross-service pip dependencies (requests, schedule, paramiko, flask, pyjwt, faker, redis, pydantic, etc.)
**Built via:** `./scripts/build_base.sh`. Used by all 24 Python service Dockerfiles.

### postgres/, nginx/
Reserved for future configs. Empty today.

## scripts/

- `build_base.sh` — builds `nebulax-python-base:latest`; no-op if already present, `--force` to rebuild
- `test_module.sh` — start core + one service and tail logs
- `dev_core.sh` — start only the core infrastructure (for native module dev)

## shared/
Empty skeletons (`python/`, `typescript/`). No code today.

## archive/
Superseded docs from prior phases. Read-only historical record.

## Context_docs/
**Frozen Dec 5 2025 snapshot for AI-agent context-loading.** Do not edit. Has its own README explaining the snapshot. Each file is a duplicate of a root-level NebulaX_*.md from that date.

## internal_notes/
Author's working notes. Gitignored.

## tests/
Sparse; testing not yet a strong story. See ROADMAP.md.

## .agent/, .gemini/, .claude/
AI-agent scratch directories. Gitignored. Do not edit by hand.
