# Changelog

Notable changes to NebulaX/OrbitGuard, newest first. For current state, see [docs/STATUS.md](docs/STATUS.md); for the future, see [docs/ROADMAP.md](docs/ROADMAP.md).

## 2026-05-16

### Fixed during validation
- **Celestrak fallback URL was returning CSV** instead of 3-line element format, causing the tracker to parse garbage (CSV header row treated as satellite name), produce NaN positions, and silently fail every TLE_UPDATE POST. Fixed `services/space-guard/tracker/main.py` to use `https://celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=tle` explicitly. With this fix the tracker emits ~27 real satellites instead of 9 garbage ones, and TLE_UPDATEs reach the core API. Without Space-Track creds, this is now the working default.
- **Enabled the silenced per-satellite error print** at `services/space-guard/tracker/main.py:474` (was commented out). Errors in the telemetry loop are now visible in logs.

### Documentation system
- New `docs/README.md` is the navigation hub for the whole doc set.
- New `docs/PROJECT.md` — one-page "what this is."
- New `docs/DEVELOPMENT.md` — three run modes, profiles, env vars, ports, credentials, common workflows, troubleshooting.
- New `docs/STATUS.md` — living "where we are + in flight" doc.
- New `docs/ROADMAP.md` — replaces the Dec 2025 `NebulaX_Master_Plan.md`.
- New `docs/PROJECT_MAP.md` — folder-by-folder catalog of every directory in the repo.
- New root `CHANGELOG.md` — this file.
- Root `README.md` rewritten as a short entry point that links into `docs/`.

### Workstream A — resource overhaul
- New `infrastructure/python-base/Dockerfile` + `requirements.txt` shared across 24 Python services. Standardizes on Python 3.11-slim (drops the prior mix of 3.9-slim / 3.10-alpine / 3.10-slim-bookworm).
- New `scripts/build_base.sh` builds the base; called automatically by `dev.sh`, `inc_cycle.sh`, `inc_space.sh`.
- All 24 service Dockerfiles rewritten to `FROM nebulax-python-base:latest`. Three keep service-specific apt steps: `vuln-scanner` (nmap), `core`/`honeypot-ssh` (system deps now in base anyway).
- Dashboard Dockerfile rewritten as multi-stage (deps → builder → runtime); `Dockerfile.dev` preserved for hot-reload-in-Docker; `docker-compose.dev.yml` override added.
- New `minimal` Compose profile (postgres, redis, core-api, dashboard, space-tracker, ground-station) — six containers, the canonical "just show me satellites" mode.
- New `dev.sh` is the canonical hybrid-dev entry point (`dev_hybrid.sh` preserved for back-compat).
- `services/core/main.py` gained a background `retention_loop` task: deletes events older than `EVENT_RETENTION_DAYS` (default 7) every 6 hours. Set `EVENT_RETENTION_DAYS=0` to disable.
- `.dockerignore` added to all 24 Python service dirs + dashboard.
- `inc_space.sh` now uses the `minimal` profile.

### Workstream B — 3D globe fix (`/space`)
- `services/dashboard/src/pages/space.js`: replaced `setSatellites(prev => ({...prev, ...new}))` merge with replace. This is the single highest-leverage fix — stops ghost satellites from accumulating after the tracker drops them.
- Removed the `DEBUG-SAT-1` fallback satellite that used to be injected on fetch failure (masked real errors).
- Orbit fetch now skips satellites with `MISSING` TLE before issuing the request, distinguishes 404 from network errors, and surfaces the failure as an `⚠ ORBIT: <reason>` indicator in the selected-sat panel.
- Polling rate slowed from 2 s → 5 s (tracker emits once per minute anyway; faster polling created noise without value).
- Cesium Ion token in `_app.js` now reads `NEXT_PUBLIC_CESIUM_ION_TOKEN` env var, falling back to the bundled local-dev token.
- `next.config.js` `reactStrictMode: false` now has a code comment explaining why (Cesium Viewer cannot survive React 18's double-invoke).

### Workstream D — polish bugs
- `services/core/schemas.py`: added missing `EventType` members that services were already publishing: `AUTH_SUCCESS`, `RANSOM_NOTE`, `FILE_ENCRYPTED`, `FORENSIC_CASE`, `FINGERPRINT_UPDATE`, `INFO`. Previously these would 422 at `/events/ingest`.
- `services/space-guard/tracker/main.py`: now reads `SPACETRACK_USER`/`SPACETRACK_PASS` (documented names) with `ST_USER`/`ST_PASS` as fallback aliases.
- `services/core/main.py`: re-enabled the Redis orbit cache (1-hour TTL keyed by sat name); logs cache HIT/MISS.
- `services/core/db/database.py`: SQLAlchemy `echo` now reads `SQL_ECHO` env var; defaults off.
- `services/core/main.py`: CORS `allow_origins` now reads `CORS_ORIGINS` (default `http://localhost:3000`); `*` allowed for lab use.
- `services/space-guard/tracker/war_detector/submodules/geo.py`: inline comment documents that LUCH/OLYMP name-matching is a placeholder; real longitude-drift tracking is on ROADMAP.

### Notes
- Two cleanup items intentionally deferred pending explicit user OK: deletion of the unreferenced root `de421.bsp` (16 MB) and `de421.bsp.download` (3 MB), and deletion/archival of `two.md` and the Dec 2025 root `NebulaX_*.md` files.
- Plan file: `~/.claude/plans/snazzy-weaving-wigderson.md`.
