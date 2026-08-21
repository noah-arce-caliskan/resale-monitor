import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { FormEvent, useState } from "react";
import {
  createWatchlist,
  getListing,
  getWatchlist,
  listWatchlists,
  runWatchlist,
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
  const [listingId, setListingId] = useState<string | null>(null);
  const active = selected ?? watches.data?.[0]?.id ?? null;
  const detail = useQuery({
    queryKey: ["watchlist", active],
    queryFn: () => getWatchlist(active!),
    enabled: !!active,
  });
  const listing = useQuery({
    queryKey: ["listing", listingId],
    queryFn: () => getListing(listingId!),
    enabled: listingId !== null,
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
            <section className="health-grid" aria-label="Source health">
              {detail.data?.source_health.map((source) => (
                <article
                  key={source.purpose}
                  className={`health health--${source.status}`}
                >
                  <span>{source.purpose}</span>
                  <b>{source.status.replace("_", " ")}</b>
                  <small>
                    {source.records_seen} records · {source.new_listings} new ·{" "}
                    {source.changed_listings} changed
                  </small>
                  {source.error_detail ? <p>{source.error_detail}</p> : null}
                </article>
              ))}
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
                  onClick={() => setListingId(item.listing_id)}
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
            {detail.data?.references.length ? (
              <details className="references">
                <summary>
                  Browse {detail.data.reference_count} reference listings
                </summary>
                <div className="reference-list">
                  {detail.data.references.map((reference) => (
                    <article key={reference.listing_id}>
                      <div>
                        <b>{reference.title}</b>
                        <small>{reference.location_text}</small>
                      </div>
                      <div>
                        <b>{money(reference.price_minor)}</b>
                        <small>
                          {reference.evidence_type.replace("_", " ")}
                        </small>
                      </div>
                    </article>
                  ))}
                </div>
              </details>
            ) : null}
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
      {listingId ? (
        <div className="dialog-backdrop">
          <article
            className="dialog listing-workspace"
            role="dialog"
            aria-label="Listing evidence"
          >
            <p className="eyebrow">Evidence workspace</p>
            {listing.isPending ? <p>Loading listing evidence…</p> : null}
            {listing.isError ? <p>Listing evidence is unavailable.</p> : null}
            {listing.data ? (
              <>
                <h2>{listing.data.title}</h2>
                <div className="evidence-metrics">
                  <div>
                    <small>Fair value</small>
                    <b>
                      {money(listing.data.fair_value_low_minor)}–
                      {money(listing.data.fair_value_high_minor)}
                    </b>
                  </div>
                  <div>
                    <small>Total cost</small>
                    <b>
                      {money(listing.data.total_cost_low_minor)}–
                      {money(listing.data.total_cost_high_minor)}
                    </b>
                  </div>
                  <div>
                    <small>Advantage</small>
                    <b>{money(listing.data.conservative_advantage_minor)}</b>
                  </div>
                  <div>
                    <small>Confidence</small>
                    <b>{Math.round(listing.data.confidence_bp / 100)}%</b>
                  </div>
                </div>
                <p>
                  This deterministic result uses labeled asking-price
                  comparisons and conservative costs. Demo evidence is not a
                  verified sale.
                </p>
                <section>
                  <h3>Extracted attributes</h3>
                  <dl className="attribute-list">
                    {Object.entries(listing.data.attributes).map(
                      ([key, value]) => (
                        <div key={key}>
                          <dt>{key.replace("_", " ")}</dt>
                          <dd>{value ?? "Unknown"}</dd>
                        </div>
                      ),
                    )}
                  </dl>
                </section>
                <section>
                  <h3>Comparable evidence</h3>
                  <div className="evidence-list">
                    {listing.data.comparables.map((comparable) => (
                      <article key={comparable.market_evidence_id}>
                        <div>
                          <b>{comparable.title}</b>
                          <small>
                            {comparable.evidence_type.replace("_", " ")} ·
                            weight{" "}
                            {Math.round(comparable.final_weight_bp / 100)}%
                          </small>
                        </div>
                        <b>{money(comparable.price_minor)}</b>
                      </article>
                    ))}
                  </div>
                </section>
                <section>
                  <h3>Cost assumptions</h3>
                  {listing.data.costs.map((cost) => (
                    <p key={cost.kind}>
                      <b>
                        {cost.kind.replace("_", " ")}: {money(cost.low_minor)}–
                        {money(cost.high_minor)}
                      </b>
                      <br />
                      {cost.rationale}
                    </p>
                  ))}
                </section>
                <section>
                  <h3>Price and availability history</h3>
                  <ol className="timeline">
                    {listing.data.observations.map((observation) => (
                      <li key={observation.observed_at}>
                        <b>{money(observation.asking_price_minor)}</b>
                        <span>
                          {observation.retrieval_outcome} ·{" "}
                          {new Date(observation.observed_at).toLocaleString()}
                        </span>
                      </li>
                    ))}
                  </ol>
                </section>
                <a
                  className="source-link"
                  href={listing.data.source_url}
                  target="_blank"
                  rel="noreferrer"
                >
                  Open source listing
                </a>
              </>
            ) : null}
            <button onClick={() => setListingId(null)}>Close</button>
          </article>
        </div>
      ) : null}
    </div>
  );
}

export default App;
