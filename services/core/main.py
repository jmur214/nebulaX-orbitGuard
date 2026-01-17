from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from contextlib import asynccontextmanager
import logging

# Import our internal modules
from db.database import engine, Base, get_db
from db.models import EventModel
from schemas import UniversalEvent

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NebulaX-Core")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle Manager:
    1. On Startup: Connect to DB and create tables.
    2. On Shutdown: Close connections.
    """
    # Create Tables (In production, use Alembic, but this is fine for MVP)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("NebulaX Core: Database Connected & Tables Synced")
    yield
    logger.info("NebulaX Core: Shutting Down")

app = FastAPI(title="NebulaX Core API", version="1.0.0", lifespan=lifespan)

# --- CRITICAL: CORS MIDDLEWARE ---
# This allows your Dashboard (running on localhost:3000) to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, lock this to ["http://localhost:3000"]
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
    # 1. Fetch all events (In prod, cache this or use aggregation queries)
    result = await db.execute(select(EventModel))
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