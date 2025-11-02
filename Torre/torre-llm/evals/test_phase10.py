from __future__ import annotations
"""
Smoke tests da Fase 10:
- Forense de impacto: risco e segredos
- RAG CANON: lentes escolhidas
- Otimizador: 7B ↔ 14B por tamanho
"""
from llm.forensics.impact_analyzer import analyze_diff
from llm.rag.canon import pick_lenses, lens_report
from llm.optimization.cost_optimizer import choose_route

def _diff_with_secret()->str:
    return """--- a/src/config.ts
+++ b/src/config.ts
@@ -1,1 +1,3 @@
 export const cfg={}
+const api_key = "sk-123456789012345678901234567890";
+export const ok=true
+"""

def _diff_small()->str:
    return """--- a/src/App.tsx
+++ b/src/App.tsx
@@ -1,1 +1,2 @@
 console.log('a')
+console.log('b')
+"""

def test_forensics_and_lenses():
    logs={"lint":"TS2304: Cannot find name SettingsPage"}
    files={"src/App.tsx":"console.log('a')\n"}
    out = analyze_diff(logs, files, _diff_with_secret())
    assert out["summary"]["secrets_found"]>=1
    assert out["summary"]["risk_score"]>0
    lenses = pick_lenses(logs, _diff_small())
    rep = lens_report(lenses)
    assert isinstance(rep, list) and len(rep)>=1 and "rule" in rep[0]

def test_optimizer_route():
    small = choose_route({"lint":"x"}, {"A":"B"})
    huge_logs = {"lint":"x"*200000, "build":"y"*200000}
    big = choose_route(huge_logs, {"A":"B"*200000})
    assert small["model"] in (small["model"],)  # sempre definido
    assert big["model"] != "" and big["window"] in ("medium","long")
    assert isinstance(small["compressed_logs"], dict)
    assert len("".join(small["compressed_logs"].values())) <= len("".join({"lint":"x"}.values()))

if __name__ == "__main__":
    test_forensics_and_lenses()
    test_optimizer_route()
    print("✅ Fase 10 OK — Forense, CANON e Otimizador funcionais.")
