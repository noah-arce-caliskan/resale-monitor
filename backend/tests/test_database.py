import pytest
from sqlalchemy import text

from resale_monitor.config import Settings
from resale_monitor.database import Database
from resale_monitor.main import create_app


def test_sqlite_connections_enforce_foreign_keys_and_wal(database_url: str) -> None:
    database = Database(database_url)

    with database.connect() as connection:
        foreign_keys = connection.execute(text("PRAGMA foreign_keys")).scalar_one()
        journal_mode = connection.execute(text("PRAGMA journal_mode")).scalar_one()

    database.dispose()

    assert foreign_keys == 1
    assert journal_mode == "wal"


def test_live_mode_requires_credentials_before_initializing_resources(
    database_url: str,
) -> None:
    with pytest.raises(ValueError, match="requires eBay client credentials"):
        create_app(Settings(database_url=database_url, source_mode="live"))
