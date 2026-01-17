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

## 3. Unit Tests
Each microservice should have its own internal unit tests.
- **Location:** `tests/` directory within each service folder.
- **Tools:** `pytest` (Python), `jest`/`vitest` (Next.js).

## 4. End-to-End (E2E) Scenarios
Simulate full attack/defense loops.
- **Hybrid Mode:** Manually run the attacker and defender scripts in separate terminals.
- **Full Docker Mode:** Use `ai-engine` or orchestration scripts to trigger events.
