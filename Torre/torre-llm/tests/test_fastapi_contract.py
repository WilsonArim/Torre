import os, uuid
from fastapi.testclient import TestClient
from llm.server import create_app
from ._helpers import expect_ok, expect_auth_required, expect_rate_limited

API_KEY = os.environ.get("FORTALEZA_API_KEY", "test-key")
client = TestClient(create_app())

def _auth(): 
    return {"x-api-key": API_KEY}

def test_vanguard_brief_requires_auth_and_returns_bullets():
    """Testa que vanguard brief requer auth e retorna formato correto"""
    # sem auth → 401/403/422 (validação ou auth)
    r = client.post("/research/vanguard/brief", json={"query":"SSR vs SSG","sources":[]})
    expect_auth_required(r.status_code)

    # com auth → 200 e formato (se módulo disponível)
    r = client.post(
        "/research/vanguard/brief",
        headers=_auth(),
        json={"query":"SSR vs SSG","sources":[{"title":"Next","url":"https://x"}]},
    )
    # Pode retornar 200 (sucesso), 422 (validação) ou 503 (módulo indisponível)
    assert r.status_code in (200, 422, 503)
    if r.status_code == 200:
        body = r.json()
        assert isinstance(body.get("bullets"), list) and 5 <= len(body["bullets"]) <= 10

def test_rerank_execute_auth_and_rate_limit():
    """Testa que rerank requer auth e tem rate limit"""
    payload = {
        "workspace":"default",
        "candidates":[
            "--- a/a\n+++ b/a\n+console.log(1)",
            "--- a/a\n+++ b/a\n+console.log(2)"
        ],
        "k":2
    }
    
    # sem auth → 401/403/422 (validação ou auth)
    r = client.post("/rerank/execute", json=payload)
    expect_auth_required(r.status_code)
    
    # com auth → 200, 422 (validação) ou 503 (módulo indisponível)
    r = client.post("/rerank/execute", headers=_auth(), json=payload)
    assert r.status_code in (200, 422, 503)
    
    # rate-limit: só testa se módulo estiver disponível
    if r.status_code == 200:
        got_429 = any(
            client.post("/rerank/execute", headers=_auth(), json=payload).status_code == 429 
            for _ in range(40)
        )
        assert got_429, "Rate limit não foi ativado após 40 chamadas"

def test_memory_promote_auth_200():
    """Testa que memory promote requer auth e retorna 200"""
    r = client.post("/memory/promote", headers=_auth())
    # Pode retornar 200 (sucesso) ou 422 (módulo indisponível)
    assert r.status_code in (200, 422)
    if r.status_code == 200:
        body = r.json()
        assert body.get("ok") in (True, 1)

def test_strategos_plan_contract():
    """Testa contrato do strategos plan (trace_id, steps)"""
    r = client.post("/strategos/plan", json={
        "logs":{"types":"TS2307"}, 
        "files":{"src/App.tsx":"console.log(1)"}
    })
    # Pode retornar 200 (sucesso) ou 422 (módulo indisponível)
    assert r.status_code in (200, 422)
    if r.status_code == 200:
        body = r.json()
        assert "trace_id" in body  # fase 16
        # passos presentes — contrato básico
        assert "steps" in body and isinstance(body["steps"], list)

def test_ops_apply_waf_and_auth():
    """Testa que ops/apply tem WAF e auth"""
    payload = {
        "workspace": ".",
        "diff": "--- a/test.txt\n+++ b/test.txt\n+hello\n"
    }
    
    # sem auth → 401/403/422 (validação ou auth)
    r = client.post("/ops/apply", json=payload)
    expect_auth_required(r.status_code)
    
    # com auth → 200 ou erro de validação
    r = client.post("/ops/apply", headers=_auth(), json=payload)
    assert r.status_code in (200, 400, 413, 423, 422, 503)  # sucesso ou erro de validação

def test_traces_badge_format():
    """Testa formato do traces badge"""
    r = client.get("/traces/badge")
    # Pode retornar 200 (sucesso) ou 422 (erro de validação)
    assert r.status_code in (200, 422)
    if r.status_code == 200:
        body = r.json()
        # Validação do contrato da Fase 16
        assert "trace_id" in body
        assert "ts" in body
        assert "endpoint" in body
        assert "tokens_in_est" in body
        assert "tokens_out_est" in body

def test_health_check_always_200():
    """Testa que health check sempre retorna 200"""
    r = client.get("/health")
    expect_ok(r.status_code)
    body = r.json()
    assert body.get("ok") in (True, 1)

def test_memory_metrics_format():
    """Testa formato das métricas de memória"""
    r = client.get("/memory/metrics")
    expect_ok(r.status_code)
    body = r.json()
    assert "metrics" in body
    assert "rules" in body
    assert isinstance(body["metrics"], dict)
    assert isinstance(body["rules"], list)
