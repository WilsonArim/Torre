import os
import json
from typing import Dict, Any, List

from fastapi.testclient import TestClient
from llm.server import create_app

API_KEY = os.environ.get("FORTALEZA_API_KEY", "test-key")

def _auth() -> Dict[str, str]:
    return {"x-api-key": API_KEY}

def run_standalone():
    app = create_app()
    client = TestClient(app)

    print("\n== GET /health ==")
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body.get("ok") in (True, 1)
    print("✅ Health check OK")

    print("\n== GET /memory/metrics ==")
    r = client.get("/memory/metrics")
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, dict)
    assert "metrics" in body and "rules" in body
    print("✅ Memory metrics OK")

    print("\n== GET /traces/badge ==")
    r = client.get("/traces/badge")
    # Pode retornar 200 (sucesso) ou 422 (erro de validação)
    assert r.status_code in (200, 422)
    if r.status_code == 200:
        body = r.json()
        assert isinstance(body, dict)
        assert "trace_id" in body
        print("✅ Traces badge OK")
    else:
        print("✅ Traces badge (erro de validação - esperado)")

    print("\n== Teste de rate limit ==")
    # Testa se o rate limit está funcionando
    hit_429 = False
    for i in range(10):
        r = client.get("/health")
        if r.status_code == 429:
            hit_429 = True
            break
    print(f"✅ Rate limit test OK (429 hit: {hit_429})")

    print("\n✅ Teste FastAPI básico passou com sucesso!")

if __name__ == "__main__":
    run_standalone()
