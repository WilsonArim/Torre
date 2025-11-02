import React, { useEffect, useRef, useState } from "react";
import { getStrategosBadge, getStrategosEvents, StrategosBadge, StrategosEvent } from "../../api/strategos";

export default function StrategosBadge() {
  const [badge, setBadge] = useState<StrategosBadge>({ mode: "NONE" });
  const [events, setEvents] = useState<StrategosEvent[] | null>(null);
  const [open, setOpen] = useState(false);
  const hoverRef = useRef<HTMLDivElement | null>(null);
  const [tick, setTick] = useState(0);

  useEffect(() => {
    let mounted = true;
    const load = async () => {
      try {
        const b = await getStrategosBadge();
        if (mounted) setBadge(b || { mode: "NONE" });
      } catch {
        /* noop */
      }
    };
    load();
    const id = setInterval(() => {
      setTick((n) => n + 1);
      load();
    }, 15000);
    return () => {
      mounted = false;
      clearInterval(id);
    };
  }, []);

  // lazy-load dos últimos eventos quando abre o hover card
  useEffect(() => {
    let mounted = true;
    const loadEv = async () => {
      try {
        const r = await getStrategosEvents(3);
        if (mounted) setEvents(r?.events || []);
      } catch {
        if (mounted) setEvents([]);
      }
    };
    if (open && events == null) loadEv();
    let id: any = null;
    if (open) {
      id = setInterval(loadEv, 15000);
    }
    return () => {
      mounted = false;
      if (id) clearInterval(id);
    };
  }, [open, events]);

  const color =
    badge.mode === "PATCH"
      ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-200"
      : badge.mode === "ADVICE"
      ? "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-200"
      : "bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-200";

  const a2g =
    typeof badge.attempts_to_green_est === "number"
      ? ` · A2G≈${badge.attempts_to_green_est.toFixed(1)}`
      : "";

  const posts1h = badge?.recent_posts_1h ?? 0;
  const posts1hText = ` · posts(1h)=${posts1h}`;

  const title =
    `Strategos: ${badge.mode}` + (badge.ts ? ` @ ${badge.ts}` : "") + (a2g ? ` (${a2g.slice(3)})` : "") + `\nPosts (últ. 1h): ${posts1h}`;

  return (
    <div
      ref={hoverRef}
      className="relative inline-block"
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
      onFocus={() => setOpen(true)}
      onBlur={() => setOpen(false)}
    >
      <span
        className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] ${color}`}
        title={title}
        aria-live="polite"
        aria-haspopup="dialog"
        aria-expanded={open}
      >
        <span className="font-medium">Strategos:</span>
        <span className="uppercase">{badge.mode}</span>
        {a2g ? <span className="opacity-70">{a2g}</span> : null}
        <span className="opacity-60">{posts1hText}</span>
      </span>

      {/* Hover Card */}
      {open ? (
        <div
          role="dialog"
          aria-label="Últimos planos do Strategos"
          className="absolute right-0 mt-2 w-96 max-w-[92vw] rounded-xl border shadow-lg bg-white/95 dark:bg-zinc-900/95 backdrop-blur px-3 py-2 z-50"
        >
          <div className="flex items-center justify-between mb-1">
            <strong className="text-xs uppercase tracking-wide opacity-70">Últimos planos (3)</strong>
            <span className="text-[10px] opacity-60">{badge.ts ? `@ ${badge.ts}` : ""}</span>
          </div>
          {!events || events.length === 0 ? (
            <div className="text-xs opacity-70">Sem planos ainda.</div>
          ) : (
            <ul className="space-y-2">
              {events.map((e, i) => (
                <li key={`${e.ts || "t"}-${i}`} className="text-[12px]">
                  <div className="flex items-center gap-2">
                    <span
                      className={`px-1.5 py-0.5 rounded text-[10px] ${
                        e.mode === "PATCH"
                          ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-200"
                          : e.mode === "ADVICE"
                          ? "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-200"
                          : "bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-200"
                      }`}
                      title={`Modo: ${e.mode}`}
                    >
                      {e.mode}
                    </span>
                    {typeof e.attempts_to_green_est === "number" ? (
                      <span className="opacity-70">A2G≈{e.attempts_to_green_est.toFixed(1)}</span>
                    ) : null}
                    <span className="text-[10px] opacity-60 ml-auto">{e.ts}</span>
                  </div>
                  {e.steps && e.steps.length ? (
                    <ul className="mt-1 ml-1.5 space-y-0.5">
                      {e.steps.slice(0, 3).map((s, j) => (
                        <li key={j} className="flex items-center gap-1 text-[11px]">
                          <span className="opacity-60">{j + 1}.</span>
                          <span className="uppercase opacity-70">{s.stage}</span>
                          <span className="opacity-60">→</span>
                          <code className="font-mono">{s.target}</code>
                          {typeof s.score === "number" ? (
                            <span className="opacity-60 ml-auto">{s.score.toFixed(2)}</span>
                          ) : null}
                        </li>
                      ))}
                    </ul>
                  ) : null}
                </li>
              ))}
            </ul>
          )}
        </div>
      ) : null}
    </div>
  );
}
