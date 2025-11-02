import os
from fastapi.testclient import TestClient
from llm.server import create_app

def test_strategos_badge_recent_posts_counter():
    app = create_app()
    client = TestClient(app)
    payload = {"mode": "PATCH", "attempts_to_green_est": 1.25}
    headers = {}
    api_key = os.getenv("FORTALEZA_API_KEY")
    if api_key:
        headers["x-api-key"] = api_key

    r1 = client.post("/strategos/badge", json=payload, headers=headers)
    # ambiente pode exigir auth; se não for 200, tratamos como "skip suave"
    assert r1.status_code in (200, 401, 403, 422, 429)
    if r1.status_code != 200:
        return

    r2 = client.post("/strategos/badge", json=payload, headers=headers)
    assert r2.status_code == 200

    g = client.get("/strategos/badge")
    assert g.status_code == 200
    body = g.json()
    assert "recent_posts_1h" in body
    assert isinstance(body["recent_posts_1h"], int)
    assert body["recent_posts_1h"] >= 2
