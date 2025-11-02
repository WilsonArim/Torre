import React, { useEffect, useState } from "react";
import { getTraceBadge, TraceBadge } from "../../api/traces";

export default function TraceBadge() {
  const [badge, setBadge] = useState<TraceBadge | null>(null);
  const [err, setErr] = useState<string | null>(null);

  async function refresh() {
    try {
      setErr(null);
      const b = await getTraceBadge();
      setBadge(b);
    } catch (e: any) {
      setErr(e?.message || String(e));
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

  const idShort = badge?.trace_id ? `…${badge.trace_id.slice(-6)}` : "—";
  const inT = badge?.tokens_in_est ?? 0;
  const outT = badge?.tokens_out_est ?? 0;
  const title =
    `Trace ${badge?.trace_id || ""}\n` +
    `ts: ${badge?.ts || ""}\n` +
    `endpoint: ${badge?.endpoint || ""}\n` +
    `latency: ${badge?.latency_ms ?? "?"} ms\n` +
    `tokens≈ in:${inT} out:${outT}`;

  return (
    <div
      className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full border text-[11px] text-zinc-700 dark:text-zinc-200"
      aria-live="polite"
      aria-label="Último trace processado"
      title={err ? `Erro: ${err}` : title}
    >
      <span className="opacity-70">Trace:</span>
      <strong className="font-medium">{idShort}</strong>
      <span className="opacity-60">·</span>
      <span className="opacity-80">in≈{inT}</span>
      <span className="opacity-60">/</span>
      <span className="opacity-80">out≈{outT}</span>
    </div>
  );
}
