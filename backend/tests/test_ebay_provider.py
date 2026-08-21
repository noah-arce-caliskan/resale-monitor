import httpx
import pytest

from resale_monitor.providers.ebay import (
    EbayClient,
    ProviderError,
    ProviderRateLimitError,
)

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
    assert listings[0].image_url == "https://i.ebayimg.com/images/first.jpg"
    assert "seller" not in listings[0].payload
    assert "postalCode" not in listings[0].payload["itemLocation"]
    assert requests[1].headers["Authorization"] == "Bearer token"
    assert requests[1].headers["X-EBAY-C-MARKETPLACE-ID"] == "EBAY_US"
    assert requests[1].url.params["filter"] == "itemLocationCountry:US"


async def test_ebay_search_raises_sanitized_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/oauth2/token"):
            return httpx.Response(200, json={"access_token": "token"})
        return httpx.Response(
            429,
            headers={"Retry-After": "60"},
            json={"errors": [{"message": "rate limit secret detail"}]},
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
        with pytest.raises(ProviderRateLimitError) as captured:
            await EbayClient("client", "secret", http=http).search(
                query="moped", purpose="reference", radius_miles=50
            )
    assert captured.value.retry_after_seconds == 60
    assert "secret detail" not in str(captured.value)


async def test_ebay_search_discards_untrusted_image_hosts() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/oauth2/token"):
            return httpx.Response(200, json={"access_token": "token"})
        item = _item("unsafe-image", "1000.00")
        item["image"] = {"imageUrl": "https://tracking.example/collect.jpg"}
        return httpx.Response(200, json={"itemSummaries": [item]})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
        listings = await EbayClient("client", "secret", http=http).search(
            query="moped", purpose="reference", radius_miles=50
        )

    assert listings[0].image_url is None


async def test_ebay_search_sanitizes_oauth_failure() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        del request
        return httpx.Response(401, json={"error_description": "secret detail"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
        with pytest.raises(ProviderError) as captured:
            await EbayClient("client", "secret", http=http).search(
                query="moped", purpose="reference", radius_miles=50
            )

    assert str(captured.value) == "eBay OAuth returned 401"
    assert "secret detail" not in str(captured.value)


async def test_ebay_search_rejects_untrusted_listing_url() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/oauth2/token"):
            return httpx.Response(200, json={"access_token": "token"})
        item = _item("unsafe-link", "1000.00")
        item["itemWebUrl"] = "https://tracking.example/collect"
        return httpx.Response(200, json={"itemSummaries": [item]})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
        with pytest.raises(ProviderError, match="invalid data"):
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
        "image": {"imageUrl": f"https://i.ebayimg.com/images/{item_id}.jpg"},
        "condition": "Used",
        "seller": {"username": "should-not-be-retained"},
    }
