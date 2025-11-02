export type TraceBadge = {
  ok?: boolean;
  trace_id: string;
  ts: string;
  endpoint: string;
  latency_ms?: number | null;
  tokens_in_est?: number;
  tokens_out_est?: number;
};

const API_BASE =
  (window as any).__FORTALEZA_API__ ||
  localStorage.getItem("fortaleza:api_base") ||
  "http://localhost:8765";

export async function getTraceBadge(): Promise<TraceBadge> {
  const r = await fetch(`${API_BASE}/traces/badge`, { method: "GET" });
  const t = await r.text();
  if (!r.ok) throw new Error(t || r.statusText);
  try {
    return JSON.parse(t);
  } catch {
    return { trace_id: "", ts: "", endpoint: "", latency_ms: null, tokens_in_est: 0, tokens_out_est: 0 };
  }
}
