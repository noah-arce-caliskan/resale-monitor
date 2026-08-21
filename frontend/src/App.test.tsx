import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, expect, it, vi } from "vitest";
import App from "./App";
import { listWatchlists } from "./api/watchlists";

const renderApp = () =>
  render(
    <QueryClientProvider
      client={
        new QueryClient({ defaultOptions: { queries: { retry: false } } })
      }
    >
      <App />
    </QueryClientProvider>,
  );

afterEach(() => vi.unstubAllGlobals());

it("creates a Hartford watchlist from the empty state", async () => {
  const fetchMock = vi
    .fn()
    .mockResolvedValueOnce(new Response("[]", { status: 200 }))
    .mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          id: "watch-1",
          name: "Mopeds near Hartford",
          center_place: "Hartford, CT",
        }),
        { status: 201 },
      ),
    )
    .mockResolvedValueOnce(
      new Response(
        JSON.stringify([
          {
            id: "watch-1",
            name: "Mopeds near Hartford",
            center_place: "Hartford, CT",
          },
        ]),
        { status: 200 },
      ),
    )
    .mockResolvedValue(
      new Response(JSON.stringify({ reference_count: 0, feed: [] }), {
        status: 200,
      }),
    );
  vi.stubGlobal("fetch", fetchMock);
  renderApp();
  await userEvent.click(
    await screen.findByRole("button", { name: "Create watchlist" }),
  );
  await userEvent.click(screen.getByRole("button", { name: "Save watchlist" }));
  expect(
    await screen.findByText("Deals worth investigating"),
  ).toBeInTheDocument();
  expect(fetchMock).toHaveBeenCalledWith(
    "/api/watchlists",
    expect.objectContaining({ method: "POST" }),
  );
});

it("runs a watchlist and opens evidence", async () => {
  const watch = { id: "watch-1", name: "Mopeds", center_place: "Hartford, CT" };
  const empty = { reference_count: 0, feed: [] };
  const populated = {
    reference_count: 5,
    feed: [
      {
        listing_id: "one",
        title: "Honda Metropolitan",
        asking_price_minor: 90000,
        image_url: "https://images.example/moped.jpg",
        opportunity_label: "promising",
        confidence_bp: 5500,
        fair_value_low_minor: null,
        conservative_advantage_minor: 45000,
      },
    ],
  };
  const fetchMock = vi.fn((url: string, init?: RequestInit) => {
    if (url.endsWith("/runs") && init?.method === "POST")
      return new Response(JSON.stringify({ records_seen: 7 }), { status: 200 });
    if (url === "/api/watchlists")
      return new Response(JSON.stringify([watch]), { status: 200 });
    return new Response(
      JSON.stringify(
        fetchMock.mock.calls.some((call) => String(call[0]).endsWith("/runs"))
          ? populated
          : empty,
      ),
      { status: 200 },
    );
  });
  vi.stubGlobal("fetch", fetchMock);
  renderApp();
  await userEvent.click(await screen.findByRole("button", { name: "Run now" }));
  await userEvent.click(
    await screen.findByRole("button", { name: /Honda Metropolitan/ }),
  );
  expect(
    screen.getByText(/Demo evidence is not a verified sale/),
  ).toBeInTheDocument();
  await userEvent.click(screen.getByRole("button", { name: "Close" }));
  expect(
    screen.queryByText(/Demo evidence is not a verified sale/),
  ).not.toBeInTheDocument();
});

it("opens and cancels the new-watchlist dialog", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue(new Response("[]", { status: 200 })),
  );
  renderApp();
  await userEvent.click(screen.getByRole("button", { name: "New watchlist" }));
  expect(
    screen.getByRole("form", { name: "Create watchlist" }),
  ).toBeInTheDocument();
  await userEvent.click(screen.getByRole("button", { name: "Cancel" }));
  expect(
    screen.queryByRole("form", { name: "Create watchlist" }),
  ).not.toBeInTheDocument();
});

it("shows an unavailable backend", async () => {
  vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("offline")));
  renderApp();
  expect(await screen.findByText("Backend unavailable")).toBeInTheDocument();
});

it("rejects a non-success API response", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue(new Response(null, { status: 500 })),
  );
  await expect(listWatchlists()).rejects.toThrow("API request failed: 500");
});
