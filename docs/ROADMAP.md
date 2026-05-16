# Where we're going

> [← docs index](README.md)

Replaces `NebulaX_Master_Plan.md` (Dec 2025). Loose buckets, not a Gantt chart — the project is a portfolio piece, not a team backlog.

## Short term (next 1–2 sessions)

- **Smoke-test the resource overhaul end-to-end.** Build the shared base, build every service against it, confirm nothing regressed. Concretely: `./scripts/build_base.sh && docker compose --profile full build && docker compose --profile minimal up` should yield a working `/space` with country-attributed satellites.
- **Decide on the `de421.bsp` and `two.md` deletions.** Both are flagged in [STATUS.md](STATUS.md) as awaiting explicit OK.
- **Archive the Dec 2025 root `NebulaX_*.md` files** into `archive/2025-12/` once happy with the new doc system.

## Medium term

- **Replace GEOSentinel name-match with real drift tracking.** Currently `services/space-guard/tracker/war_detector/submodules/geo.py:27` only flags satellites whose name contains `LUCH` or `OLYMP`. A real implementation would track longitude across cycles and flag sats that drift past stationkeeping thresholds.
- **Wire `services/ai-engine/`.** Both `soc_analyst/` and `scenario_gen/` are empty. Concrete first step would be `soc_analyst`: a polling service that batches recent `THREAT_DETECTED` events, sends them to the Anthropic API (with prompt caching, batch where it fits), and writes back a summarized `INFO` event with triage suggestions.
- **Real GNSS data.** `services/space-guard/tracker/war_detector/submodules/gnss.py` currently simulates jamming probabilistically across documented hotspots. Either scrape GPSJam.org map tiles or integrate ADS-B Exchange data.
- **Alembic migrations.** Core API still does `Base.metadata.create_all` on startup. Fine for the MVP, but if the schema ever changes meaningfully, we need a real migration tool.
- **Tighten requirements.txt across services.** Many services have unpinned deps (`requests` with no version). Audit and pin.
- **End-to-end Playwright test** for `/space` — open page, wait for satellites, click one, confirm orbit polyline renders. Catches the kinds of regressions Workstream B addressed.

## Long term

- **Real RF decoding via RTL-SDR.** `services/space-guard/rf-receiver/` currently emits random RF events on a 10-second timer. With actual hardware, capture and decode telemetry.
- **Full Active Directory simulation** in the target environment to replace the synthetic `identity-manager` generator.
- **CDM (Conjunction Data Message) and decay-prediction ingestion** from Space-Track — adjacent to OrbitGuard's existing TLE pipeline.
- **MkDocs (Material) site** on top of `docs/` if the project ever wants a browsable public docs page. Not needed for the portfolio use case.

## Explicitly out of scope

- Production hardening of intentionally-vulnerable services (target-web SQL injection, ground-sim hardcoded creds, honeypot accepting all auth). They're meant to be exploitable.
- Multi-host orchestration (Kubernetes, Swarm). Single-machine Docker Compose is the design.
- A real cyber-physical effect: the simulation does not actually attack real satellites or networks.
