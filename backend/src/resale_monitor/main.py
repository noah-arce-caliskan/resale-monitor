from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from resale_monitor import __version__
from resale_monitor.api.health import router as health_router
from resale_monitor.api.watchlists import router as watchlists_router
from resale_monitor.config import Settings
from resale_monitor.database import create_database
from resale_monitor.providers.ebay import EbayClient, FixtureEbayClient
from resale_monitor.services.ingestion import ListingProvider


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or Settings()
    database = create_database(app_settings.database_url)
    http = httpx.AsyncClient(timeout=20)
    provider: ListingProvider
    if app_settings.source_mode == "live":
        if not app_settings.ebay_client_id or not app_settings.ebay_client_secret:
            raise ValueError("Live source mode requires eBay client credentials")
        provider = EbayClient(
            app_settings.ebay_client_id,
            app_settings.ebay_client_secret,
            http=http,
        )
    else:
        provider = FixtureEbayClient()

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        yield
        await http.aclose()
        database.dispose()

    app = FastAPI(
        title="Resale Monitor API",
        version=__version__,
        lifespan=lifespan,
    )
    app.state.settings = app_settings
    app.state.database = database
    app.state.listing_provider = provider
    app.include_router(health_router)
    app.include_router(watchlists_router)
    return app


app = create_app()
