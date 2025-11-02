from __future__ import annotations
import os, shutil, tempfile
from pathlib import Path

from llm.reverse import CodeMap, HotspotMiner, CouplingSentinel, RefactorAdvisor
from llm.simulation.preflight_simulator import assess_refactor_plan

def _write(p: Path, txt: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(txt, encoding="utf-8")

def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="phase8_"))
    try:
        # projeto mínimo com violação: UI -> INFRA
        _write(tmp/"src/ui/Button.tsx", "import { cfg } from '../infra/config';\nexport const Button=()=>null;\n")
        _write(tmp/"src/infra/config.ts", "export const cfg={};\n")
        _write(tmp/"src/services/api.ts", "export const api={};\n")
        _write(tmp/"src/domain/model.ts", "export type User={id:string}\n")

        cm = CodeMap(str(tmp)).build()
        hs = HotspotMiner(str(tmp)).rank(cm)
        coup = CouplingSentinel().analyze(cm)
        plan = RefactorAdvisor().plan(cm, coup, hs)
        sim = assess_refactor_plan(plan)

        print("CodeMap stats:", cm["stats"])
        print("Violations:", coup["count"])
        print("First actions:", plan["actions"][:2])
        print("Preflight:", sim)

        # Gates mínimos
        assert coup["count"] >= 1, "Esperava pelo menos 1 violação (UI->INFRA)."
        assert plan["actions"], "Plano deve conter ações."
        assert sim["advisory_ok"] is True, f"Plano inválido: {sim}"
        print("✅ Fase 8: OK")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    raise SystemExit(main())
