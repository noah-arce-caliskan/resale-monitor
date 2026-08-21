import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import App from "./App";

function renderApp() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>,
  );
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("App", () => {
  it("shows that the local foundation is ready", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            status: "ok",
            service: "resale-monitor",
            checks: { database: "ok" },
          }),
          { status: 200, headers: { "Content-Type": "application/json" } },
        ),
      ),
    );

    renderApp();

    await screen.findByText("Foundation ready");
    expect(
      screen.getByRole("status", { name: "Application status" }),
    ).toHaveTextContent("Foundation ready");
    expect(screen.getByText("API connected")).toBeInTheDocument();
    expect(screen.getByText("Database ready")).toBeInTheDocument();
  });

  it("shows an actionable unavailable state", async () => {
    const fetchMock = vi
      .fn()
      .mockRejectedValueOnce(new Error("offline"))
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            status: "ok",
            service: "resale-monitor",
            checks: { database: "ok" },
          }),
          { status: 200, headers: { "Content-Type": "application/json" } },
        ),
      );
    vi.stubGlobal("fetch", fetchMock);

    renderApp();

    await screen.findByText("Foundation unavailable");
    expect(
      screen.getByRole("status", { name: "Application status" }),
    ).toHaveTextContent("Foundation unavailable");
    expect(
      screen.getByText("Start the API, then try the readiness check again."),
    ).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "Try again" }));
    await screen.findByText("Foundation ready");
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it("treats a non-success API response as unavailable", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(new Response(null, { status: 503 })),
    );

    renderApp();

    await screen.findByText("Foundation unavailable");
  });
});
