import React, { useEffect, useMemo, useState } from "react";
import {
  getGraphSummary,
  getStrategosPlan,
  GraphSummary,
  StrategosPlan,
  PlanStep,
} from "../../api/strategos";

export default function StrategosPanel() {
  const [summary, setSummary] = useState<GraphSummary | null>(null);
  const [plan, setPlan] = useState<StrategosPlan | null>(null);
  const [logsText, setLogsText] = useState<string>(
    '{"types":"TS2307: Cannot find module ./x.css","build":"vite build failed"}',
  );
  const [filesText, setFilesText] = useState<string>(
    '{"src/App.tsx":"console.log(1)"}',
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function refreshSummary() {
    try {
      setError(null);
      const s = await getGraphSummary();
      setSummary(s);
    } catch (e: any) {
      setError(e?.message || String(e));
    }
  }

  async function generatePlan() {
    try {
      setLoading(true);
      setError(null);
      const logs = logsText ? JSON.parse(logsText) : {};
      const files = filesText ? JSON.parse(filesText) : {};
      const p = await getStrategosPlan({ logs, files, top_k: 8 });
      setPlan(p);
    } catch (e: any) {
      setError(e?.message || String(e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refreshSummary();
  }, []);

  const topSteps: PlanStep[] = useMemo(
    () => plan?.steps?.slice(0, 20) || [],
    [plan],
  );

  return (
    <div className="space-y-4" aria-label="Painel Strategos v2">
      <div className="flex items-center gap-2">
        <strong className="text-xs uppercase tracking-wide opacity-70">
          Strategos v2
        </strong>
        <div className="flex-1" />
        <button
          onClick={refreshSummary}
          className="px-2 py-1 rounded border text-xs"
          title="Atualizar grafo"
        >
          Atualizar grafo
        </button>
      </div>

      {error ? (
        <div className="text-rose-600 dark:text-rose-300 text-xs">{error}</div>
      ) : null}

      <section className="space-y-2">
        <div className="text-sm">
          <div className="font-medium">Resumo do grafo</div>
          {summary ? (
            <div className="text-xs opacity-80">
              Nós: <b>{summary.nodes}</b>, Arestas: <b>{summary.edges}</b>
              {summary.top?.length ? (
                <ul className="mt-1 list-disc list-inside">
                  {summary.top.map((t) => (
                    <li key={t.path} className="truncate">
                      <span className="font-mono">{t.path}</span> — grau{" "}
                      <b>{t.degree}</b>
                    </li>
                  ))}
                </ul>
              ) : null}
            </div>
          ) : (
            <div className="text-xs opacity-70">Sem dados de grafo ainda.</div>
          )}
        </div>
      </section>

      <section className="space-y-2">
        <div className="text-sm font-medium">Gerar plano</div>
        <div className="grid grid-cols-1 gap-2">
          <label className="text-xs opacity-70">Logs (JSON)</label>
          <textarea
            value={logsText}
            onChange={(e) => setLogsText(e.target.value)}
            rows={4}
            className="w-full border rounded p-2 font-mono text-xs"
          />
          <label className="text-xs opacity-70">Files (JSON)</label>
          <textarea
            value={filesText}
            onChange={(e) => setFilesText(e.target.value)}
            rows={4}
            className="w-full border rounded p-2 font-mono text-xs"
          />
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={generatePlan}
            className="px-3 py-1 rounded border text-sm"
            aria-busy={loading}
          >
            {loading ? "A gerar…" : "Gerar plano"}
          </button>
          {plan ? (
            <span className="text-xs opacity-70">
              Modo: <b>{plan.mode}</b>
            </span>
          ) : null}
        </div>
      </section>

      {plan ? (
        <section className="space-y-2">
          <div className="text-sm font-medium">Passos priorizados (top 20)</div>
          <div className="overflow-auto border rounded">
            <table className="min-w-full text-xs">
              <thead className="bg-zinc-100/70 dark:bg-zinc-800/40">
                <tr>
                  <th className="text-left p-2">Etapa</th>
                  <th className="text-left p-2">Target</th>
                  <th className="text-right p-2">Score</th>
                  <th className="text-right p-2">Impacto</th>
                  <th className="text-right p-2">Risco</th>
                  <th className="text-right p-2">Custo</th>
                </tr>
              </thead>
              <tbody>
                {topSteps.map((s, i) => (
                  <tr key={`${s.stage}-${s.target}-${i}`} className="border-t">
                    <td className="p-2">{labelStage(s.stage)}</td>
                    <td
                      className="p-2 font-mono truncate max-w-[320px]"
                      title={s.target}
                    >
                      {s.target}
                    </td>
                    <td className="p-2 text-right">{fmt(s.score)}</td>
                    <td className="p-2 text-right">{fmt(s.impact)}</td>
                    <td className="p-2 text-right">{fmt(s.risk)}</td>
                    <td className="p-2 text-right">{fmt(s.cost)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="text-[11px] opacity-70">
            Ordem canónica: <b>build → types → tests → style</b>. Scores
            incorporam impacto×risco×custo + boosts por logs.
          </div>
        </section>
      ) : null}
    </div>
  );
}

function fmt(n: number) {
  if (n === undefined || n === null || Number.isNaN(n)) return "—";
  return n.toFixed(3);
}

function labelStage(s: PlanStep["stage"]) {
  switch (s) {
    case "build":
      return "Build";
    case "types":
      return "Types";
    case "tests":
      return "Tests";
    case "style":
      return "Style";
    default:
      return s;
  }
}
