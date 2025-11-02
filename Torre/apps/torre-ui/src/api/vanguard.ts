// Cliente para Vanguard Brief (Fase 11)
export type VanguardSource = {
  title?: string;
  url: string;
  date: string; // ISO ou legível
  domain?: string;
  snippet?: string;
};

export type VanguardBrief = {
  query: string;
  bullets: string[];
  citations: VanguardSource[];
  pipeline: string[];
  gates: { citations_min: number; scope: string };
  approved: boolean;
};

export type VanguardBriefResponse = {
  brief: VanguardBrief;
  validation: { ok: boolean; reasons: string[]; counts: { citations: number; bullets: number } };
  gate: { status: "pending" | "approved" | "rejected"; approved_by?: string | null; record?: any };
};

const API_BASE =
  (window as any).__TORRE_API__ ||
localStorage.getItem("torre:api_base") ||
  "http://localhost:8765";

export async function postVanguardBrief(
  query: string,
  sources: VanguardSource[] = [],
  approve = false,
  approver?: string
): Promise<VanguardBriefResponse> {
  const res = await fetch(`${API_BASE}/research/vanguard/brief`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, sources, approve, approver }),
  });
  const text = await res.text();
  const data = text ? JSON.parse(text) : null;
  if (!res.ok) throw new Error((data && (data.detail || data.message)) || res.statusText);
  return data as VanguardBriefResponse;
}
