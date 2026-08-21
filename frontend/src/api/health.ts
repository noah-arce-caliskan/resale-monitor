import type { components } from "./schema";

type ReadinessResponse = components["schemas"]["ReadinessResponse"];

export async function getReadiness(): Promise<ReadinessResponse> {
  const response = await fetch("/api/health", {
    headers: { Accept: "application/json" },
  });

  if (!response.ok) {
    throw new Error(`Readiness request failed with ${response.status}`);
  }

  return (await response.json()) as ReadinessResponse;
}
