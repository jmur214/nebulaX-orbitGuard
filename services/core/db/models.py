from sqlalchemy import Column, String, DateTime, JSON, Uuid
from sqlalchemy.dialects.postgresql import JSONB
import uuid
from datetime import datetime
from .database import Base

# JSON column type: efficient binary JSONB on PostgreSQL (production), plain
# JSON elsewhere (e.g. SQLite in the test suite). Behavior on Postgres is
# unchanged — JSONB remains the stored type.
PortableJSON = JSON().with_variant(JSONB(), "postgresql")

class EventModel(Base):
    __tablename__ = "events"

    # Primary Key (sqlalchemy.Uuid maps to native UUID on Postgres,
    # CHAR(32) elsewhere)
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Metadata (Indexed for fast searching)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    origin_module = Column(String, index=True)
    event_type = Column(String, index=True)
    severity = Column(String)
    classification = Column(String)

    # Context & Payload (Stored as efficient Binary JSON on Postgres)
    # This allows us to query deep inside the JSON later:
    # e.g. SELECT * FROM events WHERE payload->>'satellite_name' = 'NOAA-19'
    context = Column(PortableJSON)
    payload = Column(PortableJSON)
