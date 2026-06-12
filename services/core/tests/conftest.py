"""
Shared fixtures for the core-api test suite.

Tests run against an in-memory SQLite database (aiosqlite) with the FastAPI
dependency `get_db` overridden — no Postgres or Redis required. The model and
query layers are dialect-portable (see db/models.py PortableJSON), so the same
queries run JSONB-backed in production.
"""
import sys
from pathlib import Path

# Make `services/core` importable regardless of where pytest is invoked from.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from db.database import Base, get_db
import main as core_main


@pytest_asyncio.fixture
async def db_session():
    """Fresh in-memory SQLite DB per test, tables created from the models."""
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # share the single in-memory DB across connections
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session):
    """httpx client against the FastAPI app, with get_db overridden.

    ASGITransport does not run the lifespan, so no Redis/Postgres connection is
    attempted; redis_client stays None and cache paths are skipped.
    """
    async def override_get_db():
        yield db_session

    core_main.app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=core_main.app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    core_main.app.dependency_overrides.clear()


def make_event(
    event_type="INFO",
    origin_module="test.module",
    severity="INFO",
    payload=None,
    context=None,
    **meta_overrides,
):
    """Build a valid UniversalEvent request body with sane defaults."""
    event = {
        "event_meta": {
            "origin_module": origin_module,
            "event_type": event_type,
            "severity": severity,
            "classification": "SIMULATION",
            **meta_overrides,
        },
        "context": context or {},
        "payload": payload or {},
    }
    return event


# A real ISS (ZARYA) TLE — valid checksum, fine for SGP4 propagation in tests.
ISS_TLE_LINE1 = "1 25544U 98067A   24023.58668981  .00016717  00000-0  30777-3 0  9990"
ISS_TLE_LINE2 = "2 25544  51.6416 190.0095 0005950  35.7771  62.5039 15.49533759434427"
