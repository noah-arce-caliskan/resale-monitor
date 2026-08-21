export type Watchlist = { id: string; name: string; center_place: string };
export type FeedItem = {
  listing_id: string;
  title: string;
  asking_price_minor: number;
  image_url: string | null;
  opportunity_label: string;
  confidence_bp: number;
  fair_value_low_minor: number | null;
  conservative_advantage_minor: number | null;
};
export type WatchlistDetail = { reference_count: number; feed: FeedItem[] };

async function json<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, init);
  if (!response.ok) throw new Error(`API request failed: ${response.status}`);
  return response.json() as Promise<T>;
}

export const listWatchlists = () => json<Watchlist[]>("/api/watchlists");
export const getWatchlist = (id: string) =>
  json<WatchlistDetail>(`/api/watchlists/${id}`);
export const createWatchlist = (body: object) =>
  json<Watchlist>("/api/watchlists", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
export const runWatchlist = (id: string) =>
  json<{ records_seen: number }>(`/api/watchlists/${id}/runs`, {
    method: "POST",
  });
