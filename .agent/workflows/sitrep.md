---
description: Generate a Situation Report (SITREP) & Update Status
---
1. **Visual Inspection:**
   - Run `docker ps` to see what is *actually* running.
   - Check `docker logs nebulax-core` for recent errors.
2. **Documentation Check:**
   - Compare running containers against `NebulaX_Current_Status.md`.
   - If a module is running but listed as "Planned", update the status to "Active".
   - If a module is crashing, update the status to "Degraded".
3. **Report:**
   - Output a concise "SITREP" to the user summarizing the delta between the documentation and reality.
