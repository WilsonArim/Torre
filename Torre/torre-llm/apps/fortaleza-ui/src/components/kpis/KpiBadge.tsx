/* eslint-disable import/no-unresolved */
import { useEffect, useState } from "react";

import { getKpiBadge, KpiBadge, exportKpis } from "@/api/kpis";

function fmtPct(x?: number | null) {
  if (x == null) return "–";
  return `${x.toFixed(1)}%`;
}

export default function KpiBadge() {
  const [b, setB] = useState<KpiBadge>({});
  const [err, setErr] = useState<string | null>(null);
  const modeColor =
    (b.golden_sr ?? 0) >= 95 ? "bg-emerald-600" : "bg-amber-600";

  useEffect(() => {
    let alive = true;
    const tick = async () => {
      try {
        const v = await getKpiBadge();
        if (alive) setB(v);
      } catch (e: unknown) {
        if (alive) setErr(e instanceof Error ? e.message : String(e));
      }
    };
    tick();
    const id = setInterval(tick, 15000);
    return () => {
      alive = false;
      clearInterval(id);
    };
  }, []);

  const title = `KPIs • golden=${fmtPct(b.golden_sr)} • red=${fmtPct(b.redteam_rate)} • repeat=${fmtPct(b.repeat_error_rate)} • p95=${b.latency_ms_p95 ?? "–"}ms • ts=${b.ts ?? "–"}`;

  return (
    <div
      className="inline-flex items-center gap-2"
      title={err ?? title}
      aria-live="polite"
      aria-label="KPIs badge"
    >
      <span
        className={`px-2 py-0.5 rounded-full text-[11px] text-white ${modeColor}`}
      >
        KPIs: {fmtPct(b.golden_sr)} / {fmtPct(b.repeat_error_rate)}
      </span>
      <button
        className="text-[11px] underline decoration-dotted"
        onClick={async () => {
          try {
            await exportKpis();
          } catch (e) {
            // Silently handle export errors
            console.warn("Failed to export KPIs:", e);
          }
        }}
        title="Exportar KPIs do dia (JSON/CSV)"
      >
        export
      </button>
    </div>
  );
}
