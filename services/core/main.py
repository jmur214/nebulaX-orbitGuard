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

@app.get("/events/recent")
async def get_recent_events(limit: int = 20, db: AsyncSession = Depends(get_db)):
    """
    Used by the Dashboard polling loop.
    Returns the X most recent events, ordered by newest first.
    """
    try:
        # SQL: SELECT * FROM events ORDER BY timestamp DESC LIMIT {limit}
        result = await db.execute(
            select(EventModel).order_by(desc(EventModel.timestamp)).limit(limit)
        )
        events = result.scalars().all()
        return events
    except Exception as e:
        logger.error(f"Read Error: {e}")
        raise HTTPException(status_code=500, detail="Database Read Error")