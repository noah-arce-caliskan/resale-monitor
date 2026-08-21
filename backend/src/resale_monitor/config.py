from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    log_level: str = "INFO"
    data_dir: str = "./data/local"
    database_url: str = "sqlite:///./data/local/resale-monitor.sqlite3"
    source_mode: Literal["fixture", "live"] = "fixture"
    ebay_client_id: str | None = None
    ebay_client_secret: str | None = None
