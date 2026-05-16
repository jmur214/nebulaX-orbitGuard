# What this project is

> [← docs index](README.md)

NebulaX is a **cyber-physical fusion range**: a containerized simulation of a defense-contractor environment ("Astra Dynamics") under coordinated attack across both terrestrial and space domains. It exists to demonstrate, in working code, that orbital telemetry and cyber threat data can be fused into one operational picture.

The centerpiece is **OrbitGuard** — the space-domain stack:

- Ingests live NORAD TLEs from Space-Track (Celestrak fallback)
- Propagates orbits with Skyfield SGP4 from a Chicago ground station
- Trains a scikit-learn `RandomForestClassifier` on live orbital parameters (inclination + apogee) against SATCAT ground truth to attribute each satellite to a nation-state
- Runs a six-module **Space War Detector** every cycle (Maneuver, Proximity, Debris, GNSS, Launch, GEO) that fuses into a 0–100 escalation score and a DEFCON 1–5 level
- Surfaces all of it on a 3D Cesium globe with click-to-orbit polylines

Wrapped around OrbitGuard is a 7-service red team, 6-service blue team, an intentionally-vulnerable target environment, and small intel/GRC tiers — about 27 Docker containers in total. Every service publishes structured `UniversalEvent` JSON to a single FastAPI core, which persists to PostgreSQL (JSONB) and is read by a Next.js dashboard.

## Who it's for

Built solo by Jackson Murphy as a portfolio piece for security-engineering / space-cyber roles. Optimized for:

1. **Demonstrating breadth** — orbital mechanics + ML + Docker microservices + Next.js/Cesium + adversary emulation in one repo
2. **Showing the fusion thesis** — that you can correlate "satellite drifting in GEO" with "credential brute-force on the ground station" in a single dashboard

## What it explicitly is *not*

- Production software. The vulnerable services are *meant* to be exploited; do not deploy.
- A research framework. The War Detector heuristics are illustrative, not validated.
- A doc collection or tutorial. The code is the contract; docs (these and others) describe what the code is, not what it should be.

## Quick mental model

```
                     ┌──────────────────────┐
                     │  Cesium 3D Dashboard │  (Next.js, port 3000)
                     └──────────┬───────────┘
                                │ polls /events/recent
                     ┌──────────▼───────────┐
                     │   Core API (FastAPI) │  (port 8000)
                     │   /events/ingest     │
                     └──────┬──────┬────────┘
              ┌─────────────┘      └──────────────┐
       ┌──────▼──────┐                     ┌──────▼──────┐
       │ PostgreSQL  │                     │   Redis     │
       │ (events     │                     │ (orbit      │
       │  JSONB)     │                     │  cache)     │
       └─────────────┘                     └─────────────┘
              ▲                                   ▲
              │   POST UniversalEvent JSON        │
   ┌──────────┴───────────────┬───────────────────┴────────┐
   │                          │                            │
┌──▼──────┐ ┌────────┐ ┌──────▼──┐ ┌──────────┐ ┌─────────▼──┐
│ Space   │ │ Red    │ │ Blue    │ │ Target   │ │ Intel/GRC  │
│ Tracker │ │ Team   │ │ Team    │ │ Services │ │ Generators │
│ + War   │ │ (7)    │ │ (6)     │ │ (3)      │ │ (4)        │
│ Detect  │ │        │ │         │ │          │ │            │
└─────────┘ └────────┘ └─────────┘ └──────────┘ └────────────┘
```

For the full topology and event schema, read [ARCHITECTURE.md](ARCHITECTURE.md). For per-service detail, read [PROJECT_MAP.md](PROJECT_MAP.md) or [SERVICES.md](SERVICES.md). For the space domain in depth, read [ORBITGUARD.md](ORBITGUARD.md).
