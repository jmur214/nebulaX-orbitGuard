"""Event retention — prune_events_older_than()."""
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, func

from db.models import EventModel
from main import prune_events_older_than



def _utcnow_naive():
    return datetime.now(timezone.utc).replace(tzinfo=None)


async def seed_event(session, age_days: float):
    session.add(
        EventModel(
            id=uuid.uuid4(),
            timestamp=_utcnow_naive() - timedelta(days=age_days),
            origin_module="test.retention",
            event_type="INFO",
            severity="INFO",
            classification="SIMULATION",
            context={},
            payload={"age_days": age_days},
        )
    )
    await session.commit()


async def count_events(session) -> int:
    return (await session.execute(select(func.count(EventModel.id)))).scalar()


async def test_prune_deletes_only_old_events(db_session):
    await seed_event(db_session, age_days=10)   # old → pruned
    await seed_event(db_session, age_days=8)    # old → pruned
    await seed_event(db_session, age_days=6)    # recent → kept
    await seed_event(db_session, age_days=0.1)  # fresh → kept

    deleted = await prune_events_older_than(db_session, days=7)
    assert deleted == 2
    assert await count_events(db_session) == 2

    remaining = (await db_session.execute(select(EventModel))).scalars().all()
    assert all(e.payload["age_days"] < 7 for e in remaining)


async def test_prune_noop_on_fresh_data(db_session):
    await seed_event(db_session, age_days=1)
    deleted = await prune_events_older_than(db_session, days=7)
    assert deleted == 0
    assert await count_events(db_session) == 1


async def test_prune_empty_table(db_session):
    deleted = await prune_events_older_than(db_session, days=7)
    assert deleted == 0
