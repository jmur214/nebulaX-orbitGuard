"""Create the events table.

Revision ID: 0001
Revises:
Create Date: 2026-06-12

Baseline migration. Pre-Alembic deployments already have an `events` table
(created by the old `Base.metadata.create_all` startup path), so creation is
guarded with a has_table check — on those databases this revision is a no-op
that simply brings them under Alembic version control.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

# Match db/models.py PortableJSON: JSONB on Postgres, JSON elsewhere.
PortableJSON = sa.JSON().with_variant(JSONB(), "postgresql")


def upgrade() -> None:
    bind = op.get_bind()
    if inspect(bind).has_table("events"):
        return  # existing pre-Alembic deployment; adopt as-is

    op.create_table(
        "events",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("timestamp", sa.DateTime(), index=True),
        sa.Column("origin_module", sa.String(), index=True),
        sa.Column("event_type", sa.String(), index=True),
        sa.Column("severity", sa.String()),
        sa.Column("classification", sa.String()),
        sa.Column("context", PortableJSON),
        sa.Column("payload", PortableJSON),
    )


def downgrade() -> None:
    op.drop_table("events")
