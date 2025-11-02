import os
from llm.providers.router import ProvidersRouter
from llm.providers.base import ProviderRequest

def test_phase20_router_decision_basic():
    r = ProvidersRouter(".")
    logs = {"types": "TS2304: Cannot find name X"}
    files = {"src/App.tsx": "console.log(1)"}
    d = r.decide(logs, files)
    assert "stage" in d and "providers" in d
    assert isinstance(d["providers"], list) and len(d["providers"]) >= 1

def test_phase20_generate_candidates():
    r = ProvidersRouter(".")
    d = r.decide({"build":"vite error"}, {"src/main.ts":"console.log(1)"})
    req = ProviderRequest(logs={"build":"vite"}, files={"src/main.ts":"console.log(1)"})
    cands = r.generate_candidates(req, d)
    assert len(cands) >= 1
    for c in cands:
        assert c.provider and isinstance(c.diff, str)
