from __future__ import annotations
"""
Teste simples da Fase 9 — Reranker por execução
Gera 3 candidatos (base, lesson, síntese) e garante que o melhor (100% verde)
é escolhido com patch mínimo.
"""
import json
from llm.execution.reranker import Reranker

class MockPreflight:
    def run_all(self, logs, files, diff):
        # Candidato "bad" falha typecheck; "lesson" passa; "synth" passa mas é maior
        ok_apply = diff.strip().startswith("--- a/") and "\n+++ b/" in diff
        type_ok = "BAD" not in diff
        lint_ok = True
        tests_ok = "TESTFAIL" not in diff
        secrets_ok = "sk-" not in diff
        adds = sum(1 for ln in diff.splitlines() if ln.startswith("+") and not ln.startswith("+++"))
        rems = sum(1 for ln in diff.splitlines() if ln.startswith("-") and not ln.startswith("---"))
        score = sum([ok_apply, type_ok, lint_ok, tests_ok, secrets_ok]) * 1.0
        return {
            "apply_ok": ok_apply, "typecheck_ok": type_ok, "lint_ok": lint_ok,
            "tests_ok": tests_ok, "secrets_ok": secrets_ok,
            "score": score, "diff_lines": adds + rems
        }

def _diff(tag: str, body: str) -> str:
    return f"""--- a/src/App.tsx
+++ b/src/App.tsx
@@ -1,1 +1,2 @@
- console.log('hello')
+ console.log('hello')
+ // {tag} {body}
+"""

def main():
    logs = {"lint": "TS2304: Cannot find name SettingsPage"}
    files = {"src/App.tsx": "console.log('hello')\n"}
    reranker = Reranker(preflight=MockPreflight())

    def gen_base():
        # Intencionalmente ruim (falha typecheck)
        return ("base", _diff("BAD", "introduz type-error"))

    def gen_lesson():
        # Passa e é pequeno
        return ("lesson", _diff("LESSON", "corrige import/assinatura"))

    def gen_synth():
        # Passa mas é maior (pior desempate)
        big = "\n".join([f"+ // line {i}" for i in range(20)])
        return ("synth", f"""--- a/src/Big.ts
+++ b/src/Big.ts
@@ -1,1 +1,22 @@
-export const x=1
{big}
""")

    out = reranker.run(logs, files, [gen_base, gen_lesson, gen_synth])
    print(json.dumps(out, indent=2))
    assert out["winner"]["name"] == "lesson", "winner deve ser o candidato 'lesson'"
    assert out["winner"]["ok"] is True
    assert out["candidates"][0]["name"] == "lesson"  # ordenação por ok/score/menor diff
    print("✅ Fase 9 OK — Reranker escolheu o candidato 100% verde com patch mínimo.")

if __name__ == "__main__":
    main()
