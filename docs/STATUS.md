# Where we are (living doc)

> [← docs index](README.md)
>
> **Last updated:** 2026-06-12

This is the first doc to read when you (or anyone) opens the project cold. Keep it short and current. When something material changes, edit this file and append to [../CHANGELOG.md](../CHANGELOG.md).

## Where we are

NebulaX is a working prototype. The full stack runs on one machine via `./dev.sh` or `docker compose up`. The OrbitGuard space domain (the centerpiece) is functional end-to-end: live NORAD TLEs → SGP4 propagation → ML country attribution → six-module War Detector → 3D Cesium globe with click-to-orbit polylines.

Recent overhaul (2026-05-15/16) reduced the resource footprint and fixed the long-standing 3D-globe ghosting issue. The dashboard now polls every 5 s (was 2 s), satellites replace rather than merge, orbit fetch failures surface in the UI instead of silently breaking, and the dashboard image is multi-stage. All 24 Python services share a `nebulax-python-base` image to dedupe disk and rebuilds. Postgres now auto-prunes events older than 7 days (configurable, `EVENT_RETENTION_DAYS=0` disables).

## In flight

| Workstream | Status | Notes |
|---|---|---|
| Workstream B — 3D globe fix | ✅ Done 2026-05-16 | space.js state merge replaced with replace; DEBUG-SAT-1 fallback removed; orbit error UI added |
| Workstream D — small bug polish | ✅ Done 2026-05-16 | EventType enum gap, ST_USER alias, Redis cache, SQL echo, CORS, GEOSentinel comment |
| Workstream A — resource overhaul | ✅ Done 2026-05-16 | Shared Python base + 24 Dockerfiles migrated; dashboard multi-stage; `minimal` profile; event retention; `.dockerignore` everywhere; `dev.sh` is canonical |
| Workstream C — documentation system | ✅ Done 2026-06-12 | Doc system in place; stale root docs archived; `docs/` is canonical |
| de421.bsp dedup (A6) | ✅ Done 2026-06-12 | Unused root `de421.bsp` + `.download` removed (tracker keeps its own copy); Cesium dist untracked (regenerated at build) |
| Archive old root NebulaX_*.md docs | ✅ Done 2026-06-12 | Moved to tracked `archive/2025-12/` with an index README; `docs/` is now the single canonical set |

### Project overhaul (in progress)

| Phase | Status | Notes |
|---|---|---|
| Phase 0 — repo hygiene + doc consolidation | ✅ Done 2026-06-12 | ~35 MB of bloat untracked (de421 dupes, Cesium dist); stale root docs archived |
| Phase 1 — engineering foundation | ✅ Done 2026-06-12 | CI (5 jobs), 34-test pytest suite for core-api, all deps pinned, Alembic migrations replace create_all. Found+fixed a real NaN-orbit bug along the way |
| Phase 2 — DEFCON/scoring accuracy | ⏳ Planned | Reconcile the two separate DEFCON computations (core game-state vs. war-detector) into one consistent, accurate signal |
| Phase 3 — dashboard/UX | ⏳ Planned | Redesign flagged graphs, polling/lag, polish |
| Later (optional) | ⏳ Planned | Real GEOSentinel longitude-drift tracking, real GNSS data. No AI engine for now. |

## Recent changes

See [../CHANGELOG.md](../CHANGELOG.md) for the full log. Last ~5 entries:

- **2026-06-12** — Overhaul Phase 1: GitHub Actions CI (lint, tests, real-Postgres migration check, compose validation, dashboard build); 34-test pytest suite for core-api; Alembic migrations replace startup `create_all`; every `requirements.txt` fully pinned; ruff correctness lint clean; fixed NaN-orbit bug for malformed TLEs.
- **2026-06-12** — Overhaul Phase 0: removed unused root `de421.bsp` (+`.download`), untracked the auto-generated Cesium dist (~35 MB total off the index), and archived the stale Dec-2025 root `NebulaX_*.md` docs into tracked `archive/2025-12/`. `docs/` is now the single canonical doc set.
- **2026-05-16** — Documentation system landed: docs/README.md hub, PROJECT/STATUS/ROADMAP/PROJECT_MAP/DEVELOPMENT created; root README rewritten to point at docs/.
- **2026-05-16** — Workstream A complete: shared `nebulax-python-base` image, 24 service Dockerfiles migrated, dashboard multi-stage, `minimal` profile, `.dockerignore` files, postgres event retention (default 7 days).
- **2026-05-16** — Workstream D complete: `EventType` enum filled out, `SPACETRACK_USER`/`PASS` aliases, Redis orbit cache re-enabled, `SQL_ECHO` env var, `CORS_ORIGINS` env var, GEOSentinel limitation documented.
- **2026-05-16** — Workstream B complete: 3D globe state-merge bug fixed; DEBUG-SAT-1 fallback removed; orbit fetch hardened; Cesium Ion token behind env var.
- **2026-05-15** — Plan written (`~/.claude/plans/snazzy-weaving-wigderson.md`) for the four-workstream cleanup.

## Known issues (small, deferred)

- `services/ai-engine/{soc_analyst, scenario_gen}` directories exist but are empty (planned). See [ROADMAP.md](ROADMAP.md).
- `services/blue-team/sensor/`, `services/red-team/password_lab/`, `services/space-guard/rf_processor/`, `shared/python/`, `shared/typescript/`, `services/core/{api, models}/` are all empty skeleton dirs — actual code is flat in their parents. Not a bug; documented in [PROJECT_MAP.md](PROJECT_MAP.md).
- GEOSentinel "drift detection" only matches sat names (LUCH/OLYMP) — true longitude-tracking is on the roadmap.
- `Context_docs/` is a frozen Dec 5 2025 snapshot used for AI agent context-loading; do not edit. See [`../Context_docs/`](../Context_docs/).
