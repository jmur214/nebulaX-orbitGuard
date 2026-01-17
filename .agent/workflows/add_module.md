---
description: Add a new Microservice Module to NebulaX
---
1. Create the module directory in `services/<team>/<module-name>`
2. Create `Dockerfile` (Copy from `services/red-team/attack-engine/Dockerfile`)
3. Create `requirements.txt` (Must include `requests`, `pydantic`)
4. Create `main.py`
   - Must import `os`, `time`, `requests`
   - Must define `report_event()` function adhering to `UniversalEvent` schema
   - Must use `CORE_API_URL` env var
5. Update `docker-compose.yml`
   - Add service definition
   - Add to `nebulax-net` network
   - Add `depends_on: core-api`
   - Add volume mount for hot reload
6. Update `NebulaX_Current_Status.md` to list the new module
