# Quick Start Guide

## Prerequisites

| Tool | Minimum Version | Notes |
|------|----------------|-------|
| Docker Desktop | 4.x | Includes Docker Compose v2 |
| `docker compose` | v2 | Use `docker compose` (not `docker-compose`) |
| RAM | 8 GB | 16 GB recommended for `--profile full` |
| Disk | 10 GB free | Build cache + container images |

---

## 1. Clone and Configure

```bash
git clone https://github.com/YOUR_USERNAME/nebulaX-orbitGuard.git
cd nebulaX-orbitGuard
```

### Optional: Space-Track API Credentials

OrbitGuard's space tracker fetches real NORAD TLE data from [space-track.org](https://www.space-track.org). Registration is free. Without credentials, the tracker automatically falls back to Celestrak — all features work, but the catalog is smaller.

```bash
# Copy the example env file
cp .env.example .env   # or create .env manually

# Add your Space-Track credentials
SPACETRACK_USER=your_email@example.com
SPACETRACK_PASS=your_password
```

The `.env` file also contains the PostgreSQL credentials used by the Core API. The defaults work for local development:

```bash
POSTGRES_USER=admin
POSTGRES_PASSWORD=nebulax_secret
POSTGRES_DB=nebulax_core
```

---

## 2. Choose Your Deployment

NebulaX uses Docker Compose profiles to let you run any subset of the platform. Start with what you need.

### Core Only (fastest start — API + dashboard)

```bash
docker compose --profile core up --build
```

Starts: `postgres`, `redis`, `core-api`, `dashboard`

Access:
- Dashboard: `http://localhost:3000`
- Core API docs: `http://localhost:8000/docs`

---

### Space Domain (OrbitGuard)

```bash
docker compose --profile core --profile space up --build
```

Starts: core stack + `space-tracker`, `ground-station`, `rf-receiver`

Access:
- Space Command: `http://localhost:3000/space`
- Ground Station: `http://localhost:5001`

What to expect:
- The space tracker will begin fetching TLEs and publishing `TLE_UPDATE` events within ~30 seconds
- Satellites appear as colored points on the Cesium globe
- Click any satellite to load its 90-minute orbit path
- The Strategic Analysis panel shows live DEFCON and escalation score from the Space War Detector
- The space tracker trains its ML classifier at startup — the first cycle takes longer than subsequent cycles

> **Tip:** The space tracker is memory-limited to 128 MB. If it exits with OOM during ML training, the `--profile core --profile space` combination is the correct one to use (avoids running the full red/blue stack simultaneously).

---

### Incremental Start (recommended for repeated development)

The `inc_space.sh` and `inc_cycle.sh` scripts build and start the platform while pruning only dangling Docker images (not all stopped containers). This preserves layer caches between runs, dramatically reducing rebuild time and preventing disk exhaustion.

```bash
# Space domain only (incremental)
./inc_space.sh

# Full system (incremental)
./inc_cycle.sh
```

---

### Red Team Operations

```bash
docker compose --profile red up --build
```

Starts: core stack + `attack-engine`, `apt-emulator`, `ransomware-sim`, `web-injector`, `password-auditor`, `vuln-scanner`, `c2-beacon`, `honeypot`, `target-web`

What to expect:
- `AUTH_FAILURE` events begin immediately (SSH brute force)
- `VULN_REPORT` events from the vulnerability scanner (~60s)
- `EXPLOIT_SUCCESS` on SQL injection (~10–20s)
- `FILE_ENCRYPTED` from ransomware simulator (~20–60s random)
- `CREDENTIAL_CRACKED` from password auditor (after honeypot captures)
- `NETWORK_FLOW` with large exfil bursts from C2 beacon

---

### Blue Team Defensive Stack

```bash
docker compose --profile blue up --build
```

Starts: core stack + `honeypot`, `blue-sentinel`, `ids-suricata`, `edr-agent`, `net-watchdog`, `net-forensics`

> **Tip:** Blue team alone produces fewer events. Run blue + red together to observe the full detection pipeline:
> ```bash
> docker compose --profile red --profile blue up --build
> ```

---

### Full System

```bash
docker compose --profile full up --build
```

Starts all 26+ containers. Recommended RAM: 16 GB.

---

## 3. Access the Platform

| Interface | URL | Credentials |
|-----------|-----|------------|
| Fusion Center (main dashboard) | `http://localhost:3000` | See personas below |
| Space Command | `http://localhost:3000/space` | — |
| Red Team view | `http://localhost:3000/red` | — |
| Blue Team view | `http://localhost:3000/blue` | — |
| Core API (Swagger) | `http://localhost:8000/docs` | — |
| Target Web Portal | `http://localhost:8080` | `admin / [SQL injectable]` |
| Ground Station | `http://localhost:5001` | `admin / solarwinds123` |
| SSH Honeypot | `ssh -p 2222 root@localhost` | Any credentials |

### Dashboard Personas

| Persona | Role | Username | Password |
|---------|------|----------|----------|
| Director | Fusion Center | `director` | `astra` |
| Operator | Space Guard | `operator` | `orbit` |
| Analyst | Blue Team | `analyst` | `defense` |
| Syndicate | Red Team | `syndicate` | `hunter2` |

---

## 4. Verify the Platform is Running

```bash
# Check all containers are healthy
docker compose ps

# Verify the Core API is accepting events
curl http://localhost:8000/game/state

# Verify events are flowing
curl "http://localhost:8000/events/recent?limit=5"

# Check space tracker is publishing (after ~30s)
curl "http://localhost:8000/events/recent?limit=5" | python3 -m json.tool | grep event_type
```

Expected output from game state:
```json
{
  "red_score": 0,
  "blue_score": 0,
  "defcon": 5,
  "event_count": 0
}
```

After running for a few minutes with the red profile:
```json
{
  "red_score": 140,
  "blue_score": 35,
  "defcon": 4,
  "event_count": 312
}
```

---

## 5. Development Workflows

### Test a Single Service

```bash
# Start core + one specific service, stream logs
./scripts/test_module.sh ids-suricata
./scripts/test_module.sh ransomware-sim
./scripts/test_module.sh space-tracker
```

### Run a Service Locally (Hybrid Mode)

Run a service directly on your host machine against the Dockerized infrastructure:

```bash
# Start infrastructure only
./scripts/dev_core.sh

# Run service locally
cd services/red-team/ransomware-sim
pip install -r requirements.txt
CORE_HOST=localhost python main.py
```

The `CORE_HOST=localhost` override is required because the service is outside the Docker network — it communicates with Core API via localhost:8000 instead of the container name.

### Rebuild a Single Service

```bash
# Rebuild only the dashboard (useful after frontend changes)
docker compose build dashboard

# Rebuild and restart a specific service
docker compose up --build space-tracker
```

### View Logs

```bash
# All services
docker compose logs -f

# Single service
docker compose logs -f space-tracker
docker compose logs -f core-api

# Last 50 lines
docker compose logs --tail=50 space-tracker
```

---

## 6. Shutdown and Cleanup

```bash
# Graceful shutdown (Ctrl+C or:)
docker compose down

# Remove volumes (wipes the PostgreSQL event lake)
docker compose down -v

# Prune dangling images only (safe — preserves layer cache)
docker image prune -f

# Nuclear option — removes everything including build cache
docker system prune -af --volumes
```

---

## Troubleshooting

### Dashboard won't load / very slow first start

The Next.js + Cesium bundle is large (~40 MB compiled). First load compiles everything.

- Wait 60–90 seconds after the container starts before opening the browser
- Turbopack is enabled by default (10x faster than Webpack)
- The container has a 2 GB memory limit — if your host is RAM-constrained, reduce other running containers

```bash
# If Turbopack causes issues, revert to standard Next.js:
# Edit services/dashboard/package.json
# Change "dev": "next dev --turbopack" to "dev": "next dev"
docker compose build dashboard && docker compose up dashboard
```

### Space tracker exits immediately

Usually missing or invalid Space-Track credentials. Check logs:

```bash
docker compose logs space-tracker
```

If you see authentication errors, either add valid credentials to `.env` or leave them blank — the tracker will fall back to Celestrak automatically. If the fallback also fails, check your network connectivity.

### No events appearing in dashboard

```bash
# Check core-api is running and healthy
curl http://localhost:8000/docs

# Check postgres is ready
docker compose logs postgres | grep "ready to accept connections"

# Check a service is publishing
docker compose logs space-tracker | grep "Published"
docker compose logs red-attacker | grep "event"
```

### Port already in use

If another application is using port 3000, 8000, or 5432:

```bash
# Find what's using the port
lsof -i :3000

# Or change the host port mapping in docker-compose.yml
# e.g., change "3000:3000" to "3001:3000"
```

### Out of disk space

```bash
# Check Docker disk usage
docker system df

# Prune safely (keeps layer cache)
docker image prune -f
docker container prune -f

# If still tight, remove unused volumes
docker volume prune -f
```

---

## Related Documentation

- [ORBITGUARD.md](ORBITGUARD.md) — Space domain architecture, Space War Detector, ML attribution
- [ARCHITECTURE.md](ARCHITECTURE.md) — Full system architecture, event schema, API reference
- [SERVICES.md](SERVICES.md) — Per-service configuration and behavior
- [THREAT_MODELS.md](THREAT_MODELS.md) — Exercise playbooks for red/blue/fusion operations
