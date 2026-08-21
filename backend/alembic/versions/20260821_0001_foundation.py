"""Establish the migration baseline.

Revision ID: 20260821_0001
Revises:
Create Date: 2026-08-21
"""

revision: str = "20260821_0001"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    """Create the Alembic version marker for the foundation baseline."""


def downgrade() -> None:
    """Remove the foundation baseline marker through Alembic."""
