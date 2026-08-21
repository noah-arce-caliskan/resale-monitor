import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { FormEvent, useState } from "react";
import {
  createWatchlist,
  getWatchlist,
  listWatchlists,
  runWatchlist,
  type FeedItem,
} from "./api/watchlists";
import "./styles.css";

const money = (value: number | null) =>
  value === null
    ? "Insufficient evidence"
    : `$${Math.round(value / 100).toLocaleString()}`;

function App() {
  const cache = useQueryClient();
  const watches = useQuery({
    queryKey: ["watchlists"],
    queryFn: listWatchlists,
  });
  const [selected, setSelected] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [listing, setListing] = useState<FeedItem | null>(null);
  const active = selected ?? watches.data?.[0]?.id ?? null;
  const detail = useQuery({
    queryKey: ["watchlist", active],
    queryFn: () => getWatchlist(active!),
    enabled: !!active,
  });
  const create = useMutation({
    mutationFn: createWatchlist,
    onSuccess: async (item) => {
      setSelected(item.id);
      setCreating(false);
      await cache.invalidateQueries({ queryKey: ["watchlists"] });
    },
  });
  const run = useMutation({
    mutationFn: () => runWatchlist(active!),
    onSuccess: async () => {
      await cache.invalidateQueries({ queryKey: ["watchlist", active] });
    },
  });

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    create.mutate({
      name: data.get("name"),
      query: data.get("query"),
      center_place: "Hartford, CT",
      radius_miles: Number(data.get("radius")),
    });
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Resale Monitor</p>
          <h1>Market evidence for your next ride.</h1>
        </div>
        <button onClick={() => setCreating(true)}>New watchlist</button>
      </header>
      <aside className="sidebar">
        <p className="section-label">Your watchlists</p>
        {watches.data?.map((watch) => (
          <button
            className="watch"
            key={watch.id}
            onClick={() => setSelected(watch.id)}
          >
            <b>{watch.name}</b>
            <small>{watch.center_place}</small>
          </button>
        ))}
      </aside>
      <main className="workspace">
        {watches.isError ? (
          <section className="empty">
            <h2>Backend unavailable</h2>
            <p>Start the API and retry.</p>
          </section>
        ) : !active ? (
          <section className="empty">
            <p className="eyebrow">Start here</p>
            <h2>Watch Hartford’s moped market.</h2>
            <p>
              Local opportunities stay separate from nationwide price evidence.
            </p>
            <button onClick={() => setCreating(true)}>Create watchlist</button>
          </section>
        ) : (
          <>
            <section className="workspace-heading">
              <div>
                <p className="eyebrow">Hartford acquisition feed</p>
                <h2>Deals worth investigating</h2>
              </div>
              <div>
                <span>{detail.data?.reference_count ?? 0} reference comps</span>
                <button disabled={run.isPending} onClick={() => run.mutate()}>
                  {run.isPending ? "Searching…" : "Run now"}
                </button>
              </div>
            </section>
            {detail.data?.feed.length === 0 ? (
              <section className="empty compact">
                <h3>No listings collected yet</h3>
                <p>Run the watchlist to load the labeled demo dataset.</p>
              </section>
            ) : null}
            <section className="deal-grid" aria-label="Ranked deal feed">
              {detail.data?.feed.map((item) => (
                <button
                  className="deal-card"
                  key={item.listing_id}
                  onClick={() => setListing(item)}
                >
                  {item.image_url ? <img src={item.image_url} alt="" /> : null}
                  <div>
                    <span className="label">{item.opportunity_label}</span>
                    <h3>{item.title}</h3>
                    <p>
                      Ask <b>{money(item.asking_price_minor)}</b>
                    </p>
                    <p>
                      Fair value low <b>{money(item.fair_value_low_minor)}</b>
                    </p>
                    <p className="advantage">
                      Conservative advantage{" "}
                      {money(item.conservative_advantage_minor)}
                    </p>
                  </div>
                </button>
              ))}
            </section>
          </>
        )}
      </main>
      {creating ? (
        <div className="dialog-backdrop">
          <form
            className="dialog"
            aria-label="Create watchlist"
            onSubmit={submit}
          >
            <p className="eyebrow">New watchlist</p>
            <h2>Define the market.</h2>
            <label>
              Name
              <input name="name" defaultValue="Mopeds near Hartford" />
            </label>
            <label>
              Search terms
              <input name="query" defaultValue="moped scooter" />
            </label>
            <label>
              Radius
              <input name="radius" type="number" defaultValue="50" />
            </label>
            <p>
              Local results become candidates. Nationwide results are evidence
              only.
            </p>
            <div>
              <button type="button" onClick={() => setCreating(false)}>
                Cancel
              </button>
              <button type="submit">Save watchlist</button>
            </div>
          </form>
        </div>
      ) : null}
      {listing ? (
        <div className="dialog-backdrop">
          <article className="dialog">
            <p className="eyebrow">Evidence workspace</p>
            <h2>{listing.title}</h2>
            <p>Confidence {Math.round(listing.confidence_bp / 100)}%</p>
            <p>
              This deterministic result uses active asking-price comparisons and
              a conservative cost reserve. Demo evidence is not a verified sale.
            </p>
            <button onClick={() => setListing(null)}>Close</button>
          </article>
        </div>
      ) : null}
    </div>
  );
}

export default App;
