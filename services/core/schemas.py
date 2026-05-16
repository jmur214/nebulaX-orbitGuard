from pydantic import BaseModel, Field, UUID4
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum
import uuid

class EventSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class EventType(str, Enum):
    # Core
    SYSTEM_STARTUP = "SYSTEM_STARTUP"
    INFO = "INFO"
    # Space
    TLE_UPDATE = "TLE_UPDATE"
    SATELLITE_PASS = "SATELLITE_PASS"
    RF_SIGNAL_CAPTURED = "RF_SIGNAL_CAPTURED"
    FINGERPRINT_UPDATE = "FINGERPRINT_UPDATE"
    # Cyber
    SSH_AUTH_FAIL = "AUTH_FAILURE" # Standardized name
    AUTH_FAILURE = "AUTH_FAILURE"   # Alias for flexibility
    AUTH_SUCCESS = "AUTH_SUCCESS"
    EXPLOIT_SUCCESS = "EXPLOIT_SUCCESS"
    # Blue Team
    THREAT_DETECTED = "THREAT_DETECTED"
    COMMAND_EXECUTED = "COMMAND_EXECUTED"
    WEB_TRAFFIC = "WEB_TRAFFIC"
    CREDENTIAL_CRACKED = "CREDENTIAL_CRACKED"
    VULN_REPORT = "VULN_REPORT"
    NETWORK_FLOW = "NETWORK_FLOW"
    FORENSIC_CASE = "FORENSIC_CASE"
    # Red Team
    FILE_ENCRYPTED = "FILE_ENCRYPTED"
    RANSOM_NOTE = "RANSOM_NOTE"

class EventMeta(BaseModel):
    id: UUID4 = Field(default_factory=uuid.uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    origin_module: str
    event_type: EventType
    severity: EventSeverity
    classification: str = "SIMULATION"

class EventContext(BaseModel):
    related_ip: Optional[str] = None
    related_asset_id: Optional[str] = None
    mitre_attack_id: Optional[str] = None
    legal_compliance_tag: Optional[str] = None

class UniversalEvent(BaseModel):
    event_meta: EventMeta
    context: EventContext
    payload: Dict[str, Any]

class GameState(BaseModel):
    defcon: int
    red_score: int
    blue_score: int
    status: str