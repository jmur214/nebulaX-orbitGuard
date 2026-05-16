# NebulaX / OrbitGuard — Documentation

> Navigation hub. Every doc below links back here at the top.

This is a **documentation system**, not a doc pile. It's designed so that when you (or anyone) opens the repo cold, you can answer five questions in five minutes:

| Question | Read this |
|---|---|
| *What is this project?* | [PROJECT.md](PROJECT.md) |
| *Where are we right now? What's in flight?* | [STATUS.md](STATUS.md) |
| *Where are we going next?* | [ROADMAP.md](ROADMAP.md) |
| *How do I run it / work on it?* | [QUICKSTART.md](QUICKSTART.md) → [DEVELOPMENT.md](DEVELOPMENT.md) |
| *What is every folder/file for?* | [PROJECT_MAP.md](PROJECT_MAP.md) |

## Full index

**Orientation** — read first
- [PROJECT.md](PROJECT.md) — what NebulaX/OrbitGuard is, in one page
- [ARCHITECTURE.md](ARCHITECTURE.md) — system topology, event schema, profiles
- [ORBITGUARD.md](ORBITGUARD.md) — the space domain deep dive (SGP4, ML attribution, War Detector)

**Daily use** — read when working
- [QUICKSTART.md](QUICKSTART.md) — 5-minute path to a running OrbitGuard
- [DEVELOPMENT.md](DEVELOPMENT.md) — three run modes, env vars, common workflows, troubleshooting
- [PROJECT_MAP.md](PROJECT_MAP.md) — folder-by-folder catalog

**Tracking** — read to understand current state
- [STATUS.md](STATUS.md) — living doc: where we are, what's in flight
- [ROADMAP.md](ROADMAP.md) — where we're going
- [../CHANGELOG.md](../CHANGELOG.md) — what changed and when

**Deep dives** — read on demand
- [SERVICES.md](SERVICES.md) — per-service reference (all 27 containers)
- [THREAT_MODELS.md](THREAT_MODELS.md) — MITRE ATT&CK coverage, intentional vulnerabilities, exercise playbooks
- [RESUME_ASSETS.md](RESUME_ASSETS.md) — portfolio/interview framing

## How to keep the docs honest

When something changes, the **only** docs that should need updating are:

- [STATUS.md](STATUS.md) — if the current state shifted
- [ROADMAP.md](ROADMAP.md) — if priorities reordered
- [../CHANGELOG.md](../CHANGELOG.md) — append-only log
- [PROJECT_MAP.md](PROJECT_MAP.md) — if a folder was added/removed/renamed

Everything else is stable reference material. If you find yourself rewriting PROJECT/ARCHITECTURE/ORBITGUARD often, that's a smell — those describe the *what* and *why*, which shouldn't churn.

## Historical material (do not edit)

- [`../archive/`](../archive/) — superseded docs from prior phases, preserved for record.
- [`../Context_docs/`](../Context_docs/) — frozen Dec 2025 snapshot used for AI-agent context-loading.
