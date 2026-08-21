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
export type SourceHealth = {
  purpose: string;
  status: string;
  records_seen: number;
  new_listings: number;
  changed_listings: number;
  error_detail: string | null;
  finished_at: string | null;
};
export type ReferenceListing = {
  listing_id: string;
  title: string;
  price_minor: number;
  location_text: string | null;
  evidence_type: string;
};
export type WatchlistDetail = {
  reference_count: number;
  source_health: SourceHealth[];
  feed: FeedItem[];
  references: ReferenceListing[];
};
export type ListingDetail = {
  listing_id: string;
  title: string;
  source_url: string;
  provider_status: string;
  image_urls: string[];
  attributes: Record<string, string | number | null>;
  opportunity_label: string;
  confidence_bp: number;
  fair_value_low_minor: number | null;
  fair_value_midpoint_minor: number | null;
  fair_value_high_minor: number | null;
  total_cost_low_minor: number | null;
  total_cost_high_minor: number | null;
  conservative_advantage_minor: number | null;
  observations: {
    observed_at: string;
    retrieval_outcome: string;
    asking_price_minor: number | null;
    provider_status: string;
  }[];
  comparables: {
    market_evidence_id: string;
    title: string;
    price_minor: number;
    evidence_type: string;
    provider: string;
    final_weight_bp: number;
    reason_codes: string[];
  }[];
  costs: {
    kind: string;
    low_minor: number;
    high_minor: number;
    rationale: string;
  }[];
};

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
export const getListing = (id: string) =>
  json<ListingDetail>(`/api/listings/${id}`);
