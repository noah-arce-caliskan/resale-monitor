from sqlalchemy import text

from resale_monitor.database import Database


def test_sqlite_connections_enforce_foreign_keys_and_wal(database_url: str) -> None:
    database = Database(database_url)

    with database.connect() as connection:
        foreign_keys = connection.execute(text("PRAGMA foreign_keys")).scalar_one()
        journal_mode = connection.execute(text("PRAGMA journal_mode")).scalar_one()

    database.dispose()

    assert foreign_keys == 1
    assert journal_mode == "wal"
