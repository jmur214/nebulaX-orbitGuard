# NebulaX System Status

## Active Services

### Core Infrastructure
- **Core API**: `nebulax-core` (FastAPI) - The central brain.
- **Database**: `nebulax-db` (Postgres) - Persistent storage.
- **Message Bus**: `nebulax-bus` (Redis) - Event streaming.
- **Dashboard**: `nebulax-dashboard` (Next.js) - Mission Control.

### Red Team (Offense)
- **Attack Engine**: `red-attacker` - Orchestrates attacks.
- **C2 Beacon**: `nebulax-c2-beacon` - Simulates malware traffic.
- **Vuln Scanner**: `nebulax-vuln-scanner` - Finds open ports.
- **Password Auditor**: `nebulax-password-auditor` - Cracks weak credentials.
- **Ransomware Sim**: `nebulax-ransomware` - [NEW] Simulates file encryption attacks.

### Blue Team (Defense)
- **Sentinel**: `nebulax-blue-sentinel` - Detects successful exploits.
- **Honeypot**: `nebulax-honeypot` - SSH trap.
- **Net Watchdog**: `nebulax-net-watchdog` - [NEW] Monitors traffic and vuln reports.
- **Net Forensics**: `nebulax-net-forensics` - [NEW] Investigates alerts automatically.

### Space Guard
- **Tracker**: `nebulax-space-tracker` - Satellite telemetry.
- **Ground Sim**: `nebulax-ground-sim` - Ground station simulation.

### Target Environment
- **Web App**: `nebulax-target-web` - Vulnerable partner portal.