from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, text
from contextlib import asynccontextmanager
import asyncio
import logging
import redis.asyncio as redis
import os
import json

# Import our internal modules
from db.database import engine, Base, get_db, AsyncSessionLocal
from db.models import EventModel
from schemas import UniversalEvent

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NebulaX-Core")

# Global Redis Client
redis_client = None
REDIS_URL = os.getenv("REDIS_URL", "redis://nebulax-bus:6379/0")

# Event retention: delete events older than EVENT_RETENTION_DAYS every 6 hours.
# Set EVENT_RETENTION_DAYS=0 to disable cleanup entirely (unbounded growth, original behavior).
EVENT_RETENTION_DAYS = int(os.getenv("EVENT_RETENTION_DAYS", "7"))
RETENTION_LOOP_SECONDS = 6 * 60 * 60  # 6 hours


async def retention_loop():
    """Background task: prune old events on a schedule."""
    if EVENT_RETENTION_DAYS <= 0:
        logger.info("Event retention disabled (EVENT_RETENTION_DAYS=0).")
        return
    logger.info(f"Event retention enabled: keeping last {EVENT_RETENTION_DAYS} days.")
    while True:
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    text(f"DELETE FROM events WHERE timestamp < NOW() - INTERVAL '{EVENT_RETENTION_DAYS} days'")
                )
                await session.commit()
                deleted = result.rowcount or 0
                if deleted:
                    logger.info(f"Retention sweep: deleted {deleted} events older than {EVENT_RETENTION_DAYS} days.")
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.warning(f"Retention sweep failed (will retry): {e}")
        await asyncio.sleep(RETENTION_LOOP_SECONDS)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle Manager:
    1. On Startup: Connect to DB, create tables, start background retention task.
    2. On Shutdown: Cancel retention task and close connections.
    """
    # Create Tables (In production, use Alembic, but this is fine for MVP)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Connect to Redis
    global redis_client
    redis_client = redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
    await redis_client.ping()
    logger.info("NebulaX Core: Connected to Redis")

    logger.info("NebulaX Core: Database Connected & Tables Synced")

    # Start event-retention background task
    retention_task = asyncio.create_task(retention_loop())

    yield

    # Shutdown
    retention_task.cancel()
    try:
        await retention_task
    except asyncio.CancelledError:
        pass
    if redis_client:
        await redis_client.close()
    logger.info("NebulaX Core: Shutting Down")

app = FastAPI(title="NebulaX Core API", version="1.0.0", lifespan=lifespan)

# --- CORS MIDDLEWARE ---
# Default is the local dashboard origin only. Override with CORS_ORIGINS as a
# comma-separated list, e.g. CORS_ORIGINS="http://localhost:3000,https://demo.example.com".
# Use CORS_ORIGINS="*" to allow all (lab-only).
_cors_env = os.getenv("CORS_ORIGINS", "http://localhost:3000")
CORS_ORIGINS = ["*"] if _cors_env.strip() == "*" else [o.strip() for o in _cors_env.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def health_check():
    return {"status": "online", "system": "NebulaX Core"}

@app.post("/events/ingest")
async def ingest_event(event: UniversalEvent, db: AsyncSession = Depends(get_db)):
    """
    Ingests an event from Space Tracker, Red Team, or Ground Station.
    Persists it to PostgreSQL.
    """
    try:
        # 1. Convert Pydantic Schema -> SQLAlchemy Model
        new_event = EventModel(
            id=event.event_meta.id,
            timestamp=event.event_meta.timestamp,
            origin_module=event.event_meta.origin_module,
            event_type=event.event_meta.event_type.value, # Extract string from Enum
            severity=event.event_meta.severity.value,     # Extract string from Enum
            classification=event.event_meta.classification,
            context=event.context.model_dump(), # Convert nested object to Dict/JSON
            payload=event.payload               # Already a Dict
        )

        # 2. Write to DB
        db.add(new_event)
        await db.commit()
        await db.refresh(new_event)

        logger.info(f"Persisted Event: {new_event.id} | Type: {new_event.event_type}")

        return {
            "status": "persisted", 
            "event_id": str(new_event.id),
            "db_record": "created"
        }

    except Exception as e:
        logger.error(f"Failed to persist event: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Database Error")

# --- GAME STATE LOGIC ---
async def calculate_game_state(db: AsyncSession):
    """
    Calculates the current 'Wargame' score based on event history.
    This is a dynamic calculation for the prototype.
    """
    # 1. Fetch recent events only (prevents timeout on large tables)
    result = await db.execute(
        select(EventModel)
        .order_by(desc(EventModel.timestamp))
        .limit(1000)
    )
    events = result.scalars().all()

    red_score = 0
    blue_score = 0
    
    # Scoring Rules
    for e in events:
        # RED POINTS
        if e.event_type == "EXPLOIT_SUCCESS": red_score += 50
        elif e.event_type == "CREDENTIAL_CRACKED": red_score += 30
        elif e.event_type == "VULN_REPORT": red_score += 10
        
        # BLUE POINTS
        if e.event_type == "THREAT_DETECTED": blue_score += 20
        elif e.event_type == "AUTH_FAILURE": blue_score += 5
        elif e.event_type == "COMMAND_EXECUTED": blue_score += 2 # Activity bonus

    # DEFCON Logic (Simple heuristic)
    # Starts at 5. Goes down as Red Score increases.
    defcon = 5
    if red_score > 100: defcon = 4
    if red_score > 300: defcon = 3
    if red_score > 500: defcon = 2
    if red_score > 1000: defcon = 1

    return {
        "defcon": defcon,
        "red_score": red_score,
        "blue_score": blue_score,
        "status": "ACTIVE_CONFLICT" if red_score > 0 else "PEACE"
    }

@app.get("/game/state")
async def get_game_state(db: AsyncSession = Depends(get_db)):
    state = await calculate_game_state(db)
    return state

@app.get("/events/recent")
async def get_recent_events(
    limit: int = 20, 
    team: str = None, 
    exclude_type: str = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Returns recent events, optionally filtered by 'team' (red, blue, space, fusion).
    Also supports excluding a specific event type (e.g., TLE_UPDATE).
    """
    try:
        query = select(EventModel).order_by(desc(EventModel.timestamp)).limit(limit)
        
        # Team Filtering Logic
        if team:
            if team == "red":
                # Red Team sees their own actions + public knowledge
                query = query.filter(EventModel.origin_module.like("red.%"))
            elif team == "blue":
                # Blue Team sees defense + alerts
                query = query.filter(EventModel.origin_module.like("blue.%"))
            elif team == "space":
                # Space Command sees orbital data
                query = query.filter(EventModel.origin_module.like("space.%"))
            # 'fusion' sees everything (default)

        # Exclusion Logic
        if exclude_type:
            query = query.filter(EventModel.event_type != exclude_type)

        result = await db.execute(query)
        events = result.scalars().all()
        return events
    except Exception as e:
        logger.error(f"Read Error: {e}")
        raise HTTPException(status_code=500, detail="Database Read Error")


# --- ORBIT COMPUTATION (On-Demand) ---
from orbit_computer import compute_orbit_path

@app.get("/satellite/orbit")
async def get_satellite_orbit(
    sat_name: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Computes 90-minute orbit path for a satellite on-demand.
    Uses TLE data from the most recent TLE_UPDATE event for this satellite.
    """
    try:
        # 0. Check Cache First (Redis). 1-hour TTL keyed by sat name.
        cache_key = f"orbit:{sat_name}"
        if redis_client:
            cached_path = await redis_client.get(cache_key)
            if cached_path:
                path = json.loads(cached_path)
                logger.info(f"Orbit cache HIT  {sat_name} ({len(path)} pts)")
                return {
                    "sat_name": sat_name,
                    "orbit_path": path,
                    "points": len(path),
                    "duration_minutes": 90,
                    "source": "cache"
                }
            else:
                logger.info(f"Orbit cache MISS {sat_name}")

        # 1. Find most recent TLE_UPDATE for this satellite
        query = select(EventModel).filter(
            EventModel.event_type == "TLE_UPDATE",
            EventModel.payload["sat_name"].astext == sat_name
        ).order_by(desc(EventModel.timestamp)).limit(1)
        
        result = await db.execute(query)
        event = result.scalar_one_or_none()
        
        if not event:
            raise HTTPException(status_code=404, detail=f"No TLE data found for satellite: {sat_name}")
        
        # 2. Extract TLE from payload
        payload = event.payload
        tle = payload.get("tle", {})
        line1 = tle.get("line1")
        line2 = tle.get("line2")
        
        # Debug: Log which satellite's TLE we're using
        payload_sat_name = payload.get("sat_name", "UNKNOWN")
        norad_id = payload.get("norad_id", "UNKNOWN")
        logger.info(f"Orbit Request: '{sat_name}' -> Found TLE for '{payload_sat_name}' (NORAD: {norad_id})")
        logger.info(f"TLE Line1: {str(line1)[:30]}...")
        
        if not line1 or not line2 or line1 == "MISSING" or line2 == "MISSING":
            logger.error(f"Invalid TLE for {sat_name}: {tle}")
            raise HTTPException(status_code=400, detail="Invalid TLE data for satellite")
        
        # 3. Get the timestamp when this satellite's position was computed
        # This ensures the orbit path starts from the displayed position
        event_timestamp = event.timestamp
        logger.info(f"Using event timestamp: {event_timestamp}")
        
        # 4. Compute orbit path starting from the event timestamp
        orbit_path = compute_orbit_path(line1, line2, sat_name, start_time=event_timestamp)
        
        if not orbit_path:
            raise HTTPException(status_code=500, detail="Failed to compute orbit path")
        
        logger.info(f"Computed orbit path for {sat_name}: {len(orbit_path)} points")

        # Cache Result (1 Hour TTL).
        if redis_client:
            try:
                await redis_client.setex(cache_key, 3600, json.dumps(orbit_path))
            except Exception as cache_err:
                logger.warning(f"Orbit cache write failed for {sat_name}: {cache_err}")

        return {
            "sat_name": sat_name,
            "orbit_path": orbit_path,
            "points": len(orbit_path),
            "duration_minutes": 90,
            "source": "computed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Orbit computation error: {e}")
        raise HTTPException(status_code=500, detail="Orbit computation failed")