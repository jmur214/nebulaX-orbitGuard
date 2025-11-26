from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from datetime import datetime
from .database import Base

class EventModel(Base):
    __tablename__ = "events"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Metadata (Indexed for fast searching)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    origin_module = Column(String, index=True)
    event_type = Column(String, index=True)
    severity = Column(String)
    classification = Column(String)
    
    # Context & Payload (Stored as efficient Binary JSON)
    # This allows us to query deep inside the JSON later:
    # e.g. SELECT * FROM events WHERE payload->>'satellite_name' = 'NOAA-19'
    context = Column(JSONB)
    payload = Column(JSONB)