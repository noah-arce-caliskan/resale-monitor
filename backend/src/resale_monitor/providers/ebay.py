import base64
from dataclasses import dataclass
from decimal import Decimal
from typing import Any
from urllib.parse import urlparse

import httpx

TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"
SEARCH_URL = "https://api.ebay.com/buy/browse/v1/item_summary/search"


class ProviderError(RuntimeError):
    """Sanitized marketplace failure safe to persist and display."""


class ProviderRateLimitError(ProviderError):
    def __init__(self, retry_after_seconds: int | None = None) -> None:
        super().__init__("eBay Browse API rate limited the request")
        self.retry_after_seconds = retry_after_seconds


def _minor_units(value: str) -> int:
    return int(Decimal(value) * 100)


def _trusted_image_url(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = urlparse(value)
        host = (parsed.hostname or "").lower()
        port = parsed.port
    except ValueError:
        return None
    if (
        parsed.scheme == "https"
        and parsed.username is None
        and parsed.password is None
        and port in {None, 443}
        and (
            host == "i.ebayimg.com"
            or host.endswith(".ebayimg.com")
            or host.endswith(".ebaystatic.com")
        )
    ):
        return value
    return None


def _trusted_listing_url(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("missing listing URL")
    parsed = urlparse(value)
    host = (parsed.hostname or "").lower()
    if (
        parsed.scheme == "https"
        and parsed.username is None
        and parsed.password is None
        and parsed.port in {None, 443}
        and (host == "ebay.com" or host.endswith(".ebay.com"))
    ):
        return parsed._replace(query="", fragment="").geturl()
    raise ValueError("untrusted listing URL")


def _evidence_payload(item: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "itemId",
        "title",
        "itemWebUrl",
        "price",
        "shippingOptions",
        "image",
        "additionalImages",
        "condition",
        "shortDescription",
        "categories",
        "buyingOptions",
        "itemCreationDate",
        "itemEndDate",
    }
    payload = {key: item[key] for key in allowed if key in item}
    location = item.get("itemLocation")
    if isinstance(location, dict):
        payload["itemLocation"] = {
            key: location[key]
            for key in ("city", "stateOrProvince", "country")
            if key in location
        }
    return payload


@dataclass(frozen=True)
class ProviderListing:
    provider_listing_id: str
    title: str
    canonical_url: str
    asking_price_minor: int
    shipping_price_minor: int
    currency: str
    location_text: str
    image_url: str | None
    condition: str | None
    payload: dict[str, Any]


class EbayClient:
    def __init__(
        self, client_id: str, client_secret: str, *, http: httpx.AsyncClient
    ) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._http = http

    async def search(
        self, *, query: str, purpose: str, radius_miles: int
    ) -> list[ProviderListing]:
        token = await self._application_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
        }
        filters = "itemLocationCountry:US"
        if purpose == "acquisition":
            filters = ",".join(
                [
                    "pickupCountry:US",
                    "pickupPostalCode:06103",
                    f"pickupRadius:{radius_miles}",
                    "pickupRadiusUnit:mi",
                    "deliveryOptions:{SELLER_ARRANGED_LOCAL_PICKUP}",
                ]
            )
        url: str | None = SEARCH_URL
        params: dict[str, str] | None = {"q": query, "limit": "50", "filter": filters}
        listings: list[ProviderListing] = []
        for _ in range(3):
            if url is None:
                break
            try:
                response = await self._http.get(url, params=params, headers=headers)
            except httpx.HTTPError as error:
                raise ProviderError("eBay Browse API is unavailable") from error
            if response.status_code == 429:
                retry_header = response.headers.get("Retry-After")
                retry_after = (
                    int(retry_header)
                    if retry_header and retry_header.isdigit()
                    else None
                )
                raise ProviderRateLimitError(retry_after)
            if response.status_code >= 400:
                raise ProviderError(f"eBay Browse API returned {response.status_code}")
            try:
                payload = response.json()
                if not isinstance(payload, dict):
                    raise ValueError("invalid response object")
                summaries = payload.get("itemSummaries", [])
                if not isinstance(summaries, list):
                    raise ValueError("invalid item summaries")
                listings.extend(_normalize(item) for item in summaries)
            except (ArithmeticError, KeyError, TypeError, ValueError) as error:
                raise ProviderError("eBay Browse API returned invalid data") from error
            url = payload.get("next")
            if url is not None and not isinstance(url, str):
                raise ProviderError("eBay Browse API returned invalid pagination data")
            params = None
        return listings

    async def _application_token(self) -> str:
        credentials = base64.b64encode(
            f"{self._client_id}:{self._client_secret}".encode()
        ).decode()
        try:
            response = await self._http.post(
                TOKEN_URL,
                headers={
                    "Authorization": f"Basic {credentials}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data={
                    "grant_type": "client_credentials",
                    "scope": "https://api.ebay.com/oauth/api_scope",
                },
            )
        except httpx.HTTPError as error:
            raise ProviderError("eBay OAuth is unavailable") from error
        if response.status_code >= 400:
            raise ProviderError(f"eBay OAuth returned {response.status_code}")
        try:
            token = response.json()["access_token"]
        except (KeyError, TypeError, ValueError) as error:
            raise ProviderError("eBay OAuth returned invalid data") from error
        if not isinstance(token, str) or not token:
            raise ProviderError("eBay OAuth returned invalid data")
        return token


class FixtureEbayClient:
    async def search(
        self, *, query: str, purpose: str, radius_miles: int
    ) -> list[ProviderListing]:
        del query, radius_miles
        prices = (
            [900_00, 1300_00]
            if purpose == "acquisition"
            else [
                1500_00,
                1700_00,
                1850_00,
                2100_00,
                2400_00,
            ]
        )
        prefix = "local" if purpose == "acquisition" else "reference"
        return [
            ProviderListing(
                provider_listing_id=f"fixture-{prefix}-{index}",
                title=f"Honda Metropolitan 50cc scooter #{index}",
                canonical_url=f"https://www.ebay.com/itm/fixture-{prefix}-{index}",
                asking_price_minor=price,
                shipping_price_minor=0,
                currency="USD",
                location_text="Hartford, CT"
                if purpose == "acquisition"
                else "United States",
                image_url="/demo-moped.svg",
                condition="Used",
                payload={"fixture": True, "purpose": purpose, "price_minor": price},
            )
            for index, price in enumerate(prices, start=1)
        ]


def _normalize(item: dict[str, Any]) -> ProviderListing:
    price = item["price"]
    shipping_options = item.get("shippingOptions") or []
    shipping = shipping_options[0].get("shippingCost", {}) if shipping_options else {}
    location = item.get("itemLocation") or {}
    location_text = ", ".join(
        value
        for value in [location.get("city"), location.get("stateOrProvince")]
        if value
    )
    image = item.get("image") or {}
    return ProviderListing(
        provider_listing_id=str(item["itemId"]),
        title=str(item["title"]),
        canonical_url=_trusted_listing_url(item["itemWebUrl"]),
        asking_price_minor=_minor_units(str(price["value"])),
        shipping_price_minor=_minor_units(str(shipping.get("value", "0"))),
        currency=str(price["currency"]),
        location_text=location_text,
        image_url=_trusted_image_url(image.get("imageUrl")),
        condition=item.get("condition"),
        payload=_evidence_payload(item),
    )
