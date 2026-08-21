from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Connection, make_url
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import ConnectionPoolEntry


class Database:
    def __init__(self, database_url: str) -> None:
        self._prepare_sqlite_directory(database_url)
        self.engine = create_engine(database_url)
        self._session_factory = sessionmaker(self.engine, expire_on_commit=False)

        if self.engine.dialect.name == "sqlite":
            event.listen(self.engine, "connect", self._configure_sqlite)

    @staticmethod
    def _prepare_sqlite_directory(database_url: str) -> None:
        url = make_url(database_url)
        if url.drivername != "sqlite" or not url.database or url.database == ":memory:":
            return

        Path(url.database).expanduser().resolve().parent.mkdir(
            parents=True, exist_ok=True
        )

    @staticmethod
    def _configure_sqlite(dbapi_connection: object, _: ConnectionPoolEntry) -> None:
        cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
        try:
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
        finally:
            cursor.close()

    @contextmanager
    def connect(self) -> Iterator[Connection]:
        with self.engine.connect() as connection:
            yield connection

    @contextmanager
    def session(self) -> Iterator[Session]:
        with self._session_factory() as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    def is_ready(self) -> bool:
        try:
            with self.connect() as connection:
                connection.execute(text("SELECT 1"))
        except Exception:
            return False
        return True

    def dispose(self) -> None:
        self.engine.dispose()


def create_database(database_url: str) -> Database:
    return Database(database_url)
