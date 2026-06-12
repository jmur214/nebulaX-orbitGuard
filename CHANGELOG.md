# Changelog

Notable changes to NebulaX/OrbitGuard, newest first. For current state, see [docs/STATUS.md](docs/STATUS.md); for the future, see [docs/ROADMAP.md](docs/ROADMAP.md).

## 2026-06-12

### Project overhaul — Phase 1 (engineering foundation)
- **CI pipeline** (`.github/workflows/ci.yml`, 5 jobs): ruff lint, core-api pytest suite, Alembic migration check against a real Postgres 15 service container (fresh upgrade + idempotency + schema sanity), `docker compose config` validation for both compose files, and a full Next.js dashboard build.
- **First real test suite**: 34 tests in `services/core/tests/` covering event ingest + pydantic validation, `/events/recent` team/exclude/limit filtering, game-state scoring + every DEFCON threshold (pinned as a safety net for the Phase 2 scoring reconciliation), event retention, `orbit_computer`, and `/satellite/orbit` (happy path, 404, bad-TLE 400, multi-sat JSON-path lookup). Runs against in-memory SQLite in <1 s — no Postgres/Redis needed.
- **Bug found by the new tests, fixed**: Skyfield does not raise on malformed TLEs — it silently produces NaN coordinates, which `/satellite/orbit` would have serialized as invalid JSON and broken the dashboard. `orbit_computer.py` now validates positions and treats NaN as failure (same failure class as the 2026-05-16 Celestrak CSV bug).
- **Alembic migrations** replace `Base.metadata.create_all` at startup. Baseline revision adopts existing pre-Alembic databases (no-ops if `events` exists). Async env.py reads `DATABASE_URL` — one source of truth with `db/database.py`. Validated on fresh DBs, pre-existing DBs, and via the in-app startup path.
- **Dialect-portable persistence layer** (production behavior on Postgres unchanged): `models.py` uses `JSON().with_variant(JSONB, "postgresql")` + `sa.Uuid`; the orbit lookup uses `.as_string()` instead of Postgres-only `.astext`; the retention sweep is a portable SQLAlchemy `delete()` (extracted as testable `prune_events_older_than()`).
- **All dependencies pinned**: `requests`/`schedule` in four services, `pandas`/`scikit-learn`/`matplotlib`/`numpy` in the tracker, `numpy` exact-pinned in core. Added `services/core/requirements-dev.txt` for test tooling.
- **Lint baseline**: new root `ruff.toml` (correctness rules only: syntax errors, undefined names, unused imports); removed ~56 unused imports across the services. The codebase is ruff-clean under the enforced rules.

### Project overhaul — Phase 0 (repo hygiene & doc consolidation)
- **Removed unused root ephemeris files** `de421.bsp` and `de421.bsp.download` (~20 MB). Only `services/space-guard/tracker/de421.bsp` is referenced (`tracker/main.py:30` `load('de421.bsp')`); the root copies were unreferenced duplicates.
- **Untracked the Cesium runtime dist** under `services/dashboard/public/cesium/` (430 files, ~15 MB). These are regenerated at build from the `cesium` npm package by `Dockerfile`, `Dockerfile.dev`, and `.devcontainer/post-create.sh`, so tracking them was redundant. Added to `.gitignore`; files remain on disk and every build path still recreates them.
- **Archived the stale Dec-2025 root docs.** `NebulaX_AI_Handoff.md`, `NebulaX_Current_Status.md`, `NebulaX_Master_Plan.md`, `NebulaX_Resume_Assets.md`, `NebulaX_System_Context.md` moved to `archive/2025-12/` (kept tracked, with an index README). `docs/` is now the single canonical doc set. `Context_docs/` and the tracker ephemeris were left untouched.
- **Clarified DEFCON intent:** DEFCON is *kept*; the old "remove the game elements" note in the Dec-2025 status doc does not reflect current intent. Phase 2 will make DEFCON scoring accurate and consistent (it is currently computed in two unrelated places).

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
