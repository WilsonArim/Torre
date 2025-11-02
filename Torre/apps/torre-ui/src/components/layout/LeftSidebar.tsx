import React, { useEffect, useMemo, useState } from "react";
import Sparkline from "../charts/Sparkline";
import VanguardWidget from "../vanguard/VanguardWidget";
import MemoryPanel from "../memory/MemoryPanel";
import StrategosPanel from "../strategos/StrategosPanel";
import StrategosBadge from "../strategos/StrategosBadge";
import TraceBadge from "../strategos/TraceBadge";
import KpiBadge from "../kpis/KpiBadge";

type Tab = "tree" | "pipeline" | "vanguard" | "memory" | "strategos";

export default function LeftSidebar() {
  const [tab, setTab] = useState<Tab>("tree");

  return (
    <aside className="w-80 border-r border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 flex flex-col">
      <div className="border-b border-zinc-200 dark:border-zinc-800">
        <div className="flex items-center justify-between">
        <nav className="flex">
          <button
            className={`flex-1 px-3 py-2 text-sm focus:outline-none focus-visible:ring rounded-none ${
              tab === "pipeline"
                ? "border-b-2 border-blue-600 font-medium"
                : "text-zinc-500"
            }`}
            onClick={() => setTab("pipeline")}
            aria-pressed={tab === "pipeline"}
            aria-controls="ls-pipeline"
            title="Pipeline de desenvolvimento"
          >
            Pipeline
          </button>
          <button
            className={`flex-1 px-3 py-2 text-sm focus:outline-none focus-visible:ring rounded-none ${
              tab === "tree"
                ? "border-b-2 border-blue-600 font-medium"
                : "text-zinc-500"
            }`}
            onClick={() => setTab("tree")}
            aria-pressed={tab === "tree"}
            aria-controls="ls-tree"
            title="Árvore inteligente do projeto"
          >
            Árvore
          </button>
          <button
            className={`flex-1 px-3 py-2 text-sm focus:outline-none focus-visible:ring rounded-none ${
              tab === "vanguard"
                ? "border-b-2 border-blue-600 font-medium"
                : "text-zinc-500"
            }`}
            onClick={() => setTab("vanguard")}
            aria-pressed={tab === "vanguard"}
            aria-controls="ls-vanguard"
            title="Pesquisa Vanguarda (engenharia-only)"
          >
            Vanguarda
          </button>
          <button
            className={`flex-1 px-3 py-2 text-sm focus:outline-none focus-visible:ring rounded-none ${
              tab === "memory"
                ? "border-b-2 border-blue-600 font-medium"
                : "text-zinc-500"
            }`}
            onClick={() => setTab("memory")}
            aria-pressed={tab === "memory"}
            aria-controls="ls-memory"
            title="Memória episódica (workspace)"
          >
            Memória
          </button>
          <button
            className={`flex-1 px-3 py-2 text-sm focus:outline-none focus-visible:ring rounded-none ${
              tab === "strategos"
                ? "border-b-2 border-blue-600 font-medium"
                : "text-zinc-500"
            }`}
            onClick={() => setTab("strategos")}
            aria-pressed={tab === "strategos"}
            aria-controls="ls-strategos"
            title="Priorização com grafo (Strategos v2)"
          >
            Strategos
          </button>
        </nav>
        <div className="px-2 py-1 flex items-center gap-2">
          <StrategosBadge />
          <TraceBadge />
          <KpiBadge />
        </div>
        </div>
      </div>
      <div className="p-3 text-sm">
        {tab === "pipeline" ? (
          <div id="ls-pipeline">
            <p className="mb-2 opacity-70">
              Pipeline (placeholder). Integração futura com API para mostrar progresso das fases.
            </p>
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-xs">Fase 0-11: Concluídas</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                <span className="text-xs">Fase 12-18: Pendentes</span>
              </div>
            </div>
          </div>
        ) : tab === "tree" ? (
          <div id="ls-tree">
            <p className="mb-2 opacity-70">
              Árvore (placeholder). Integração futura com API para listar ficheiros do workspace.
            </p>
            <ul className="font-mono text-[12px] space-y-1">
              <li>apps/fortaleza-ui/src/App.tsx</li>
              <li>apps/fortaleza-ui/src/components/…</li>
              <li>fortaleza_core/…</li>
              <li>.fortaleza/plans/…</li>
            </ul>
          </div>
        ) : tab === "vanguard" ? (
          <div id="ls-vanguard" className="space-y-3">
            <VanguardWidget />
          </div>
        ) : tab === "memory" ? (
          <MemoryPanel />
        ) : (
          <StrategosPanel />
        )}
      </div>
    </aside>
  );
}
