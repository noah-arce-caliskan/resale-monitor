import { useQuery } from "@tanstack/react-query";

import { getReadiness } from "./api/health";
import "./styles.css";

function App() {
  const readiness = useQuery({
    queryKey: ["readiness"],
    queryFn: getReadiness,
    retry: false,
  });

  const ready = readiness.isSuccess;

  return (
    <main className="shell">
      <section className="intro" aria-labelledby="page-title">
        <p className="eyebrow">Resale Monitor</p>
        <h1 id="page-title">Buy secondhand with evidence, not guesswork.</h1>
        <p className="lede">
          The local application foundation is connected from the React interface
          through the FastAPI service to SQLite.
        </p>

        <div
          className={`status-card ${ready ? "status-card--ready" : ""}`}
          role="status"
          aria-label="Application status"
        >
          <div>
            <p className="status-label">Local status</p>
            <h2>
              {readiness.isPending
                ? "Checking foundation"
                : ready
                  ? "Foundation ready"
                  : "Foundation unavailable"}
            </h2>
          </div>

          {ready ? (
            <ul className="checks" aria-label="Readiness checks">
              <li>API connected</li>
              <li>Database ready</li>
            </ul>
          ) : readiness.isError ? (
            <div className="unavailable">
              <p>Start the API, then try the readiness check again.</p>
              <button type="button" onClick={() => void readiness.refetch()}>
                Try again
              </button>
            </div>
          ) : (
            <p className="checking">Verifying the API and database…</p>
          )}
        </div>
      </section>
    </main>
  );
}

export default App;
