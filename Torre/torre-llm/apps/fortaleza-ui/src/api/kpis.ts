export type KpiBadge = {
  ts?: string | null;
  golden_sr?: number | null;
  redteam_rate?: number | null;
  repeat_error_rate?: number | null;
  requests_today?: number | null;
  latency_ms_p95?: number | null;
};

const BASE =
  (import.meta as { env?: { VITE_API_BASE?: string } }).env?.VITE_API_BASE ||
  "/";

export async function getKpiBadge(): Promise<KpiBadge> {
  const r = await fetch(`${BASE}kpis/badge`);
  if (!r.ok) throw new Error(`kpis/badge: ${r.status}`);
  return r.json();
}

export async function postKpiBadge(badge: KpiBadge, apiKey?: string) {
  const r = await fetch(`${BASE}kpis/badge`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(apiKey ? { "x-api-key": apiKey } : {}),
    },
    body: JSON.stringify(badge),
  });
  if (!r.ok) throw new Error(`post kpis/badge: ${r.status}`);
  return r.json();
}

export async function exportKpis(format: "json" | "csv" = "json") {
  const r = await fetch(`${BASE}kpis/export?format=${format}`);
  if (!r.ok) throw new Error(`kpis/export: ${r.status}`);
  return r.json();
}
