// Cliente para métricas de Memória Episódica
export type MemoryMetrics = {
  repeat_error_rate: number;   // %
  rules_promoted: number;
  rules_hit_rate: number;      // %
  avoidance_saves: number;
};

export type MemoryRule = {
  key: string;
  confidence: number;
  hits: number;
  regressions: number;
  policy: string;
  created_at: string;
};

export type MemoryResponse = {
  metrics: MemoryMetrics;
  rules: MemoryRule[];
};

const API_BASE =
  (window as any).__FORTALEZA_API__ ||
  localStorage.getItem("fortaleza:api_base") ||
  "http://localhost:8765";

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { ...(init || {}) });
  const text = await res.text();
  let data: any = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text;
  }
  if (!res.ok) throw new Error((data && (data.detail || data.message)) || res.statusText);
  return data as T;
}

export async function getMemoryMetrics(): Promise<MemoryResponse> {
  return req<MemoryResponse>("/memory/metrics", { method: "GET" });
}

export type PromoteResponse = {
  ok: boolean;
  promoted: number;
  rules: MemoryRule[];
  error?: string;
};

export async function promoteMemoryRules(): Promise<PromoteResponse> {
  return req<PromoteResponse>("/memory/promote", { method: "POST" });
}
