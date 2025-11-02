from __future__ import annotations
"""
Smoke tests da Fase 11 (Pesquisa 'Vanguarda'):
- Brief com ≥3 citações com data
- Escopo técnico
- Admin gate para CANON
"""
from llm.research.vanguard_brief import generate_brief, validate_brief
from llm.research.admin_gate import propose_to_canon

SOURCES_OK = [
    {"title":"Next.js 15 release notes","url":"https://nextjs.org/blog/next-15","date":"2025-05-15","domain":"nextjs.org","snippet":"What's new"},
    {"title":"React 19 RC","url":"https://react.dev/blog/2025/rc","date":"2025-06-10","domain":"react.dev","snippet":"RC notes"},
    {"title":"Vite 6 perf guide","url":"https://vite.dev/perf","date":"2025-04-02","domain":"vite.dev","snippet":"Perf tips"},
    {"title":"TypeScript 5.5 features","url":"https://typescript.org/docs","date":"2025-03-20","domain":"typescript.org","snippet":"New features"},
    {"title":"Webpack 6 migration","url":"https://webpack.js.org/migrate","date":"2025-02-15","domain":"webpack.js.org","snippet":"Migration guide"},
    {"title":"ESLint 9.0 breaking changes","url":"https://eslint.org/blog/9.0","date":"2025-01-10","domain":"eslint.org","snippet":"Breaking changes"},
]

def test_brief_and_gate_ok():
    brief = generate_brief("SSR vs SSG for dashboard", SOURCES_OK)
    v = validate_brief(brief)
    assert v["ok"], f"Validation failed: {v}"
    gate = propose_to_canon(brief, approver="admin@example.com", approve=True)
    assert gate["status"] == "approved"
    assert gate["record"] and gate["record"]["kind"] == "VANGUARD_BRIEF"

def test_brief_rejected_when_citations_low():
    bad = generate_brief("SSR vs SSG", SOURCES_OK[:2])  # só 2
    v = validate_brief(bad)
    assert not v["ok"] and "citations<3" in v["reasons"]
    gate = propose_to_canon(bad, approver="admin@example.com", approve=True)
    assert gate["status"] == "rejected"

if __name__ == "__main__":
    test_brief_and_gate_ok()
    test_brief_rejected_when_citations_low()
    print("✅ Fase 11 OK — Brief + citações + admin gate.")
