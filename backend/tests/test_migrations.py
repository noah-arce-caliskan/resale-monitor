from pathlib import Path

from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine, inspect

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

    command.downgrade(config, "20260821_0001")
    engine = create_engine(database_url)
    with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        assert context.get_current_revision() == "20260821_0001"
        assert "watchlists" not in inspect(connection).get_table_names()
    engine.dispose()

    command.upgrade(config, "head")
    engine = create_engine(database_url)
    with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        assert context.get_current_revision() == "6a3fd871238f"
        assert "watchlists" in inspect(connection).get_table_names()
    engine.dispose()
