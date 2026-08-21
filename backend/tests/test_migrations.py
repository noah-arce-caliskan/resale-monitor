from pathlib import Path

from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine

from alembic import command


def test_foundation_database_upgrades_to_head(
    database_url: str,
    monkeypatch,
) -> None:
    backend_dir = Path(__file__).parents[1]
    monkeypatch.setenv("DATABASE_URL", database_url)
    config = Config(backend_dir / "alembic.ini")

    command.upgrade(config, "head")

    engine = create_engine(database_url)
    with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        assert context.get_current_revision() == "6a3fd871238f"
    engine.dispose()
