# NebulaX Testing Strategy

## Overview
This document outlines the strategy for testing the NebulaX-OrbitGuard system, adhering to the project's specific storage-constrained workflows.

## 1. Development Workflows

### A. The "Hybrid" Workflow (Default)
**Use for:** Daily development, debugging, and feature implementation.
**Concept:** Run infrastructure in Docker, but code natively to save disk space and enable hot-reloading.

**Steps:**
1. **Start Infrastructure:**
   ```bash
   docker compose up -d postgres redis
   ```
2. **Run Core API (Native):**
   ```bash
   cd services/core
   # Ensure env var CORE_HOST="localhost" is set if needed, or rely on defaults
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```
3. **Run Dashboard (Native):**
   ```bash
   cd services/dashboard
   npm run dev
   ```
4. **Run Agents/Services (Native):**
   Navigate to the service directory and run `python main.py`.

### B. The "Test & Nuke" Workflow (Verification)
**Use for:** Pre-commit verification, full integration testing.
**Concept:** Builds the entire Docker stack, allows for testing, and then aggressively cleans up all images and cache to reclaim storage.

**Command:**
```bash
./test_cycle.sh
```
*Warning: This will delete all project images and build cache upon exit.*

## 2. Health Checks
We have a script to verify system status. It supports both workflows.

**Run Health Check:**
```bash
python3 tests/health_check.py
```

## 3. Unit / API Tests

The core service has a real pytest suite (34 tests) covering event ingest +
validation, `/events/recent` filtering, game-state scoring + DEFCON thresholds,
event retention, orbit computation, and the `/satellite/orbit` endpoint.

**Run it:**
```bash
cd services/core
pip install -r requirements.txt -r requirements-dev.txt
python -m pytest
```

It runs against in-memory SQLite (no Postgres/Redis needed) and finishes in
under a second — see `services/core/tests/conftest.py`.

Other microservices should grow their own suites over time:
- **Location:** `tests/` directory within each service folder.
- **Tools:** `pytest` (Python), `jest`/`vitest` (Next.js).

## 3b. Continuous Integration

`.github/workflows/ci.yml` runs on every PR and push to `main`:
- **Lint** — `ruff check .` (correctness rules only; config in `ruff.toml`)
- **Core API tests** — the pytest suite above
- **Migrations** — `alembic upgrade head` against a real Postgres 15 service
  container (fresh + idempotency + schema sanity check)
- **Compose validation** — `docker compose config` for both compose files
- **Dashboard build** — `npm ci && next build`

## 3c. Database migrations

The core API now applies **Alembic** migrations at startup (replacing the old
`Base.metadata.create_all`). Existing databases are adopted automatically — the
baseline revision no-ops if the `events` table already exists. To create a new
migration after editing `services/core/db/models.py`:

```bash
cd services/core
DATABASE_URL=postgresql+asyncpg://admin:nebulax_secret@localhost:5432/nebulax_core \
  alembic revision --autogenerate -m "describe the change"
```

## 4. End-to-End (E2E) Scenarios
Simulate full attack/defense loops.
- **Hybrid Mode:** Manually run the attacker and defender scripts in separate terminals.
- **Full Docker Mode:** Use `ai-engine` or orchestration scripts to trigger events.
