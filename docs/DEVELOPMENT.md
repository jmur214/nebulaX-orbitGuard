# Developing on NebulaX

> [← docs index](README.md)

This is the "how to interact with the thing" doc. Three run modes, all profiles, every env var, the table of ports and credentials, and the recipes for common changes.

## The three run modes

| Mode | Command | When to use | Dashboard iteration speed |
|---|---|---|---|
| **Hybrid (default)** | `./dev.sh` | Daily development | ~16 s — fastest |
| **Docker dev** | `docker compose -f docker-compose.yml -f docker-compose.dev.yml up` | You need everything in Docker but still want hot reload | ~273 s cold, then hot reload |
| **Docker prod** | `docker compose up` (with a profile) | Portable demo, performance test | n/a — production build |

### Hybrid mode — recommended

`./dev.sh` starts postgres + redis + core-api + the space stack in Docker, then prints a one-liner to run the dashboard on your host. Source-volume mounts mean code changes hot-reload without Docker rebuilds.

Useful flags:

```bash
./dev.sh --no-space          # just core stack, no space-tracker / ground-sim / rf-receiver
./dev.sh --no-tail           # don't follow logs at the end
./dev.sh --auto-dashboard    # also spawn "npm run dev" in services/dashboard in the background
./dev.sh --minimal           # use the "minimal" Compose profile (6 containers)
./dev.sh --help
```

First invocation triggers `scripts/build_base.sh` automatically (builds the shared `nebulax-python-base` image). Subsequent runs are no-ops on that step.

### Docker dev mode — hot reload inside the container

If you need everything inside Docker (e.g. testing networking, demoing to someone without Node installed) but still want hot reload:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

This swaps the dashboard to use `services/dashboard/Dockerfile.dev` (the pre-A3 behavior: `npm run dev`, source mounted as a volume).

### Docker prod mode — lighter image

```bash
docker compose --profile minimal up      # 6 containers, just OrbitGuard
docker compose --profile core up         # core + dashboard
docker compose --profile full up         # all 27 containers
```

This uses the multi-stage `services/dashboard/Dockerfile` that produces a smaller image and runs `npm run start` (production-style, no hot reload).

## Compose profiles

| Profile | Containers | When |
|---|---|---|
| `minimal` | postgres, redis, core-api, dashboard, space-tracker, ground-station | "Just show me the satellites" — the OrbitGuard demo path |
| `core` | postgres, redis, core-api, dashboard | Backend only, no domain services |
| `space` | + space-tracker, ground-station, rf-receiver | Full space stack |
| `red` | + 7 red-team services + target environment | Adversary emulation |
| `blue` | + 6 blue-team detection services | Defensive stack |
| `target` | target services only | If you're attacking from outside the compose net |
| `intel` | cve-feeder, ioc-manager | Threat-intel generators |
| `grc` | incident-reporter, policy-mapper | Compliance/reporting |
| `full` | All of the above | Full demo |

## Environment variables

Set in `.env` at repo root.

### Core API (`services/core/`)

| Var | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://admin:nebulax_secret@nebulax-db:5432/nebulax_core` | Postgres connection |
| `REDIS_URL` | `redis://nebulax-bus:6379/0` | Redis pub/sub + orbit cache |
| `EVENT_RETENTION_DAYS` | `7` | Auto-prune events older than N days. **Set to `0` to disable** (unbounded growth, original behavior). |
| `SQL_ECHO` | `false` | Set `true` to log every SQL statement (very noisy). |
| `CORS_ORIGINS` | `http://localhost:3000` | Comma-separated allowed origins. `*` allows all. |

### Space tracker (`services/space-guard/tracker/`)

| Var | Default | Purpose |
|---|---|---|
| `SPACETRACK_USER` | unset | Space-Track.org account (optional; without it the tracker falls back to Celestrak). |
| `SPACETRACK_PASS` | unset | Space-Track.org password. |
| `ST_USER`, `ST_PASS` | unset | Legacy aliases for the above. Use `SPACETRACK_*` going forward. |
| `CORE_HOST` | `nebulax-core` | Where to POST events. |

### Dashboard (`services/dashboard/`)

| Var | Default | Purpose |
|---|---|---|
| `NEXT_PUBLIC_API_HOST` | `http://localhost:8000` | Core API base URL for browser-side fetches. |
| `NEXT_PUBLIC_CESIUM_ION_TOKEN` | bundled local-dev token | Override to use your own Cesium Ion account. |

### Postgres / Redis

Configured by `docker-compose.yml`. Postgres credentials default to `admin / nebulax_secret`, override with `POSTGRES_USER` / `POSTGRES_PASSWORD`.

## Ports & demo credentials

| Service | Host port | Notes |
|---|---|---|
| Dashboard | 3000 | Cesium 3D globe at `/space`, fusion at `/fusion` |
| Core API | 8000 | Swagger at `/docs` |
| Postgres | 5432 | `admin / nebulax_secret`, db `nebulax_core` |
| Redis | 6379 | No auth |
| Ground Station | 5001 | Vulnerable login: `admin / solarwinds123` |
| Target Web Portal | 8080 | SQL injection at `/login`, flag `flag{astra_master_key_xyz}` |
| SSH Honeypot | 2222 | Accepts any credentials |

### Dashboard demo logins (`services/dashboard/src/context/AuthContext.js`)

| Username | Password | Role | Default route |
|---|---|---|---|
| `director` | `astra` | FUSION | `/fusion` |
| `operator` | `orbit` | SPACE_CMD | `/space` |
| `analyst` | `defense` | BLUE_TEAM | `/blue` |
| `syndicate` | `hunter2` | RED_TEAM | `/red` |

## Common workflows

### "I changed a Python service — how do I see my change?"

If you're using `./dev.sh`, source is volume-mounted into the container, so most services pick up changes on the next loop tick (services use `python -u` for unbuffered output). For services that don't auto-reload, restart just that container:

```bash
docker compose restart space-tracker
```

If you changed `requirements.txt`, rebuild that one service:

```bash
docker compose build space-tracker && docker compose up -d space-tracker
```

### "I changed the dashboard code"

If you're running it on the host (`npm run dev` in `services/dashboard/`), Next.js hot-reloads. No further action.

If you're in Docker dev mode, hot reload happens inside the container — usually 2–4 s. If it doesn't, the volume mount may be stale; `docker compose restart dashboard`.

### "I changed `requirements.txt` of the shared base"

Rebuild the base, then any service that depends on it:

```bash
./scripts/build_base.sh --force
docker compose build
```

### "Postgres is filling up disk"

Either lower `EVENT_RETENTION_DAYS` in `.env` (default 7) or `docker compose down -v` to nuke the volume entirely (loses history).

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| 3D globe blank / "INITIALIZING ORBITAL ENGINE…" forever | Cesium assets not copied into `public/cesium` | Check `services/dashboard/Dockerfile:21` (multi-stage build) or `Dockerfile.dev:15` |
| No satellites on `/space` after 60 s | Space tracker isn't running, or core API isn't reachable from your browser | `docker compose logs space-tracker` ; verify `NEXT_PUBLIC_API_HOST` |
| Satellite clicks 404 on `/satellite/orbit` | Selected sat has no recent TLE event | This now surfaces as "No recent TLE for this satellite" in the right panel (fixed in B3) |
| `core-api` logs flooding with SQL | `SQL_ECHO=true` is set | unset or set to `false` |
| `docker compose build` taking forever | Base image not built or stale | `./scripts/build_base.sh --force` |
| Dashboard rebuild in Docker takes 4+ minutes | You're in Docker prod mode editing source | Switch to `./dev.sh` (host) or Docker dev mode |
| `psql … FATAL: connection limit exceeded` | Lots of services trying to connect to postgres on first boot | Wait 5 s for healthcheck; postgres has retry loop |

## What to read next

- [PROJECT_MAP.md](PROJECT_MAP.md) — folder-by-folder catalog of the whole repo
- [STATUS.md](STATUS.md) — current state of the system
- [ARCHITECTURE.md](ARCHITECTURE.md) — the event schema and how data flows
