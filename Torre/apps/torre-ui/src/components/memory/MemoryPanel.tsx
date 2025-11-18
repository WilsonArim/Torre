import React, { useEffect, useState } from "react";
import {
  getMemoryMetrics,
  promoteMemoryRules,
  type MemoryResponse,
} from "../../api/memory";

export default function MemoryPanel() {
  const [data, setData] = useState<MemoryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [promoting, setPromoting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  async function refresh() {
    try {
      setLoading(true);
      setError(null);
      setNotice(null);
      const r = await getMemoryMetrics();
      setData(r);
    } catch (e: any) {
      setError(e?.message || String(e));
    } finally {
      setLoading(false);
    }
  }

  async function promote() {
    try {
      setPromoting(true);
      setError(null);
      const res = await promoteMemoryRules();
      if (!res.ok) {
        throw new Error(res.error || "Falha ao promover regras");
      }
      setNotice(`Regras promovidas: ${res.promoted}`);
      // refresh para refletir novas regras/métricas
      await refresh();
    } catch (e: any) {
      setError(e?.message || String(e));
    } finally {
      setPromoting(false);
    }
  }

  useEffect(() => {
    let mounted = true;
    refresh();
    const id = setInterval(() => mounted && refresh(), 15000);
    return () => {
      mounted = false;
      clearInterval(id);
    };
  }, []);

  const metrics = data?.metrics;
  const rules = data?.rules || [];

  return (
    <div className="space-y-3" id="ls-memory">
      <div className="flex items-center gap-2">
        <strong className="text-xs uppercase tracking-wide opacity-70">
          Memória
        </strong>
        <div className="flex-1" />
        <button
          onClick={refresh}
          className="px-2 py-1 rounded border text-xs"
          aria-busy={loading}
          title="Atualizar agora"
        >
          {loading ? "A atualizar…" : "Atualizar"}
        </button>
        <button
          onClick={promote}
          className="px-2 py-1 rounded border text-xs"
          aria-busy={promoting}
          disabled={promoting}
          title="Promover regras a partir dos episódios"
        >
          {promoting ? "A promover…" : "Promover regras"}
        </button>
      </div>

      {error ? (
        <div className="text-rose-600 dark:text-rose-300 text-xs">{error}</div>
      ) : null}
      {notice ? (
        <div className="text-emerald-600 dark:text-emerald-300 text-xs">
          {notice}
        </div>
      ) : null}

      <div className="grid grid-cols-2 gap-2">
        <MetricCard
          label="Repeat error rate"
          value={metrics ? `${metrics.repeat_error_rate}%` : "—"}
        />
        <MetricCard
          label="Rules promoted"
          value={metrics ? String(metrics.rules_promoted) : "—"}
        />
        <MetricCard
          label="Rules hit rate"
          value={metrics ? `${metrics.rules_hit_rate}%` : "—"}
        />
        <MetricCard
          label="Avoidance saves"
          value={metrics ? String(metrics.avoidance_saves) : "—"}
        />
      </div>

      <div>
        <div className="mb-1 text-xs uppercase tracking-wide opacity-70">
          Regras (read-only)
        </div>
        {rules.length === 0 ? (
          <div className="text-sm opacity-70">Sem regras promovidas ainda.</div>
        ) : (
          <div className="overflow-auto border rounded">
            <table className="w-full text-sm">
              <thead className="bg-zinc-50 dark:bg-zinc-800/50">
                <tr>
                  <Th>Key</Th>
                  <Th>Conf.</Th>
                  <Th>Hits</Th>
                  <Th>Regressions</Th>
                  <Th>Policy</Th>
                  <Th>Created</Th>
                </tr>
              </thead>
              <tbody>
                {rules.map((r) => (
                  <tr key={r.key} className="border-t">
                    <Td className="font-mono text-[12px]">{r.key}</Td>
                    <Td>{(r.confidence ?? 0).toFixed(2)}</Td>
                    <Td>{r.hits ?? 0}</Td>
                    <Td className={r.regressions ? "text-rose-600" : ""}>
                      {r.regressions ?? 0}
                    </Td>
                    <Td>{r.policy || "apply_priors"}</Td>
                    <Td className="text-[12px] opacity-70">{r.created_at}</Td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="p-3 rounded border bg-white/60 dark:bg-zinc-900/60">
      <div className="text-xs opacity-70">{label}</div>
      <div className="text-lg font-semibold">{value}</div>
    </div>
  );
}

function Th({ children }: { children: React.ReactNode }) {
  return (
    <th className="text-left px-2 py-1 text-xs font-medium uppercase tracking-wide">
      {children}
    </th>
  );
}
function Td({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return <td className={`px-2 py-2 ${className}`}>{children}</td>;
}
