import React, { useState } from "react";
import {
  postVanguardBrief,
  VanguardBriefResponse,
  VanguardSource,
} from "../../api/vanguard";

export default function VanguardWidget() {
  const [query, setQuery] = useState(
    "SSR vs SSG para dashboard (Next.js/React)",
  );
  const [sourcesJson, setSourcesJson] = useState<string>(() =>
    JSON.stringify(
      [
        {
          title: "Next.js 15 release notes",
          url: "https://nextjs.org/blog/next-15",
          date: "2025-05-15",
          domain: "nextjs.org",
        },
        {
          title: "React 19 RC",
          url: "https://react.dev/blog/2025/rc",
          date: "2025-06-10",
          domain: "react.dev",
        },
        {
          title: "Vite 6 perf guide",
          url: "https://vite.dev/perf",
          date: "2025-04-02",
          domain: "vite.dev",
        },
      ],
      null,
      2,
    ),
  );
  const [approve, setApprove] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [resp, setResp] = useState<VanguardBriefResponse | null>(null);

  async function onGenerate() {
    setLoading(true);
    setError(null);
    setResp(null);
    try {
      let sources: VanguardSource[] = [];
      try {
        const parsed = JSON.parse(sourcesJson);
        if (Array.isArray(parsed)) sources = parsed as VanguardSource[];
      } catch {
        // mantém vazio → servidor pode tentar radar
      }
      const r = await postVanguardBrief(query, sources, approve);
      setResp(r);
    } catch (e: any) {
      setError(e?.message || String(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <strong className="text-xs uppercase tracking-wide opacity-70">
          Vanguarda
        </strong>
        <div className="flex-1" />
        <label className="text-xs flex items-center gap-1">
          <input
            type="checkbox"
            checked={approve}
            onChange={(e) => setApprove(e.target.checked)}
          />
          Aprovar para CANON
        </label>
      </div>
      <label className="block text-xs opacity-70">
        Pergunta (engenharia-only)
      </label>
      <input
        className="w-full border rounded px-2 py-1 text-sm"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Ex.: SSR vs SSG para dashboard em produção"
      />
      <label className="block text-xs opacity-70">
        Fontes (JSON opcional: url+date obrigatórios)
      </label>
      <textarea
        className="w-full border rounded px-2 py-1 text-xs font-mono"
        rows={6}
        value={sourcesJson}
        onChange={(e) => setSourcesJson(e.target.value)}
      />
      <button
        onClick={onGenerate}
        className="px-3 py-1 rounded border text-sm"
        aria-busy={loading}
        disabled={loading}
        title="Gerar Vanguard Brief"
      >
        {loading ? "A gerar…" : "Gerar Brief"}
      </button>
      {error ? (
        <div className="text-rose-600 dark:text-rose-300 text-xs">{error}</div>
      ) : null}
      {resp ? (
        <div className="space-y-2">
          <div>
            <strong className="text-sm">Brief</strong>
            <ul className="mt-1 list-disc ml-5 text-sm">
              {(resp.brief.bullets || []).map((b, i) => (
                <li key={i}>{b}</li>
              ))}
            </ul>
          </div>
          <div>
            <strong className="text-sm">Citações</strong>
            <ul className="mt-1 list-disc ml-5 text-xs">
              {(resp.brief.citations || []).map((c, i) => (
                <li key={i}>
                  <a
                    className="underline"
                    href={c.url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    {c.title || c.url}
                  </a>{" "}
                  — {c.domain || ""} ({c.date})
                </li>
              ))}
            </ul>
          </div>
          <div className="text-xs opacity-70">
            Validação:{" "}
            {resp.validation.ok
              ? "OK"
              : `Falhou (${resp.validation.reasons.join(", ")})`}{" "}
            · Gate: {resp.gate.status}
          </div>
        </div>
      ) : null}
    </div>
  );
}
