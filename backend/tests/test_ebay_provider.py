import httpx
import pytest

from resale_monitor.providers.ebay import EbayClient

pytestmark = pytest.mark.anyio


async def test_ebay_search_authenticates_paginates_and_normalizes() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path.endswith("/oauth2/token"):
            return httpx.Response(
                200, json={"access_token": "token", "expires_in": 7200}
            )
        if request.url.params.get("offset") == "1":
            return httpx.Response(
                200, json={"itemSummaries": [_item("second", "1800.00")]}
            )
        return httpx.Response(
            200,
            json={
                "itemSummaries": [_item("first", "1200.00")],
                "next": "https://api.ebay.com/buy/browse/v1/item_summary/search?q=moped&offset=1",
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
        listings = await EbayClient("client", "secret", http=http).search(
            query="moped", purpose="reference", radius_miles=50
        )

    assert [listing.provider_listing_id for listing in listings] == ["first", "second"]
    assert listings[0].asking_price_minor == 120_000
    assert listings[0].shipping_price_minor == 10_00
    assert listings[0].image_url == "https://images.example/first.jpg"
    assert requests[1].headers["Authorization"] == "Bearer token"
    assert requests[1].headers["X-EBAY-C-MARKETPLACE-ID"] == "EBAY_US"
    assert requests[1].url.params["filter"] == "itemLocationCountry:US"


async def test_ebay_search_raises_sanitized_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/oauth2/token"):
            return httpx.Response(200, json={"access_token": "token"})
        return httpx.Response(429, json={"errors": [{"message": "rate limit"}]})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
        with pytest.raises(RuntimeError, match="eBay Browse API returned 429"):
            await EbayClient("client", "secret", http=http).search(
                query="moped", purpose="reference", radius_miles=50
            )


def _item(item_id: str, price: str) -> dict[str, object]:
    return {
        "itemId": item_id,
        "title": "Honda Metropolitan 50cc scooter",
        "itemWebUrl": f"https://www.ebay.com/itm/{item_id}",
        "price": {"value": price, "currency": "USD"},
        "shippingOptions": [{"shippingCost": {"value": "10.00", "currency": "USD"}}],
        "itemLocation": {"city": "Hartford", "stateOrProvince": "CT"},
        "image": {"imageUrl": f"https://images.example/{item_id}.jpg"},
        "condition": "Used",
    }
