// Cliente para Strategos v2 (grafo + plano)
// - GET  /graph/summary
// - POST /strategos/plan

export type GraphTop = { path: string; degree: number };
export type GraphSummary = { nodes: number; edges: number; top: GraphTop[] };

export type StrategosWeights = {
  impact?: number;
  risk?: number;
  cost?: number;
};
export type StrategosBoosts = {
  build?: number;
  types?: number;
  tests?: number;
  style?: number;
};

export type PlanStep = {
  stage: "build" | "types" | "tests" | "style";
  target: string;
  score: number;
  impact: number;
  risk: number;
  cost: number;
  exit_criteria: string[];
};

export type StrategosPlan = {
  mode: "PATCH" | "ADVICE";
  weights: Required<StrategosWeights>;
  boosts: Required<StrategosBoosts>;
  nodes_considered: string[];
  steps: PlanStep[];
};

export type StrategosBadge = {
  mode: "PATCH" | "ADVICE" | "NONE";
  attempts_to_green_est?: number;
  ts?: string;
  recent_posts_1h?: number;
};

export type StrategosEventStep = {
  stage: string;
  target: string;
  score?: number;
};
export type StrategosEvent = {
  mode: "PATCH" | "ADVICE" | "NONE";
  attempts_to_green_est?: number;
  ts?: string;
  steps?: StrategosEventStep[];
};

const API_BASE =
  (window as any).__TORRE_API__ ||
  localStorage.getItem("torre:api_base") ||
  "http://localhost:8765";

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
  });
  const text = await r.text();
  let data: any = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text;
  }
  if (!r.ok)
    throw new Error((data && (data.detail || data.message)) || r.statusText);
  return data as T;
}

export async function getGraphSummary(): Promise<GraphSummary> {
  return req<GraphSummary>("/graph/summary", { method: "GET" });
}

export async function getStrategosPlan(payload: {
  logs?: Record<string, any>;
  files?: Record<string, string>;
  top_k?: number;
  weights?: StrategosWeights;
}): Promise<StrategosPlan> {
  return req<StrategosPlan>("/strategos/plan", {
    method: "POST",
    body: JSON.stringify(payload || {}),
  });
}

export async function getStrategosBadge(): Promise<StrategosBadge> {
  return req<StrategosBadge>("/strategos/badge", { method: "GET" });
}

export async function postStrategosBadge(
  badge: StrategosBadge,
): Promise<{ ok: boolean }> {
  return req<{ ok: boolean }>("/strategos/badge", {
    method: "POST",
    body: JSON.stringify(badge),
  });
}

export async function getStrategosEvents(
  limit = 3,
): Promise<{ events: StrategosEvent[] }> {
  return req<{ events: StrategosEvent[] }>(
    `/strategos/events?limit=${encodeURIComponent(limit)}`,
    {
      method: "GET",
    },
  );
}
