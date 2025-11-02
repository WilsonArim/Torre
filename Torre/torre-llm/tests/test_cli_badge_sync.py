import json
import os

import pytest
import llm.cli as cli


class _DummyResp:
    def __enter__(self): return self
    def read(self): return b"{}"
    def __exit__(self, exc_type, exc, tb): return False


def test_badge_sync_posts_without_thread(monkeypatch):
    """
    Quando FORT_BADGE_SYNC=1, o POST deve ocorrer de forma síncrona
    e nenhuma thread deve ser criada.
    """
    calls = {"n": 0}

    def fake_urlopen(req, timeout=1.8):
        calls["n"] += 1
        calls["url"] = req.full_url
        calls["headers"] = dict(req.headers)
        calls["data"] = req.data
        return _DummyResp()

    # Se alguma thread for criada, falhe o teste.
    def fail_thread(*a, **k):
        raise AssertionError("Thread não deveria ser criada com FORT_BADGE_SYNC=1")

    monkeypatch.setenv("FORT_BADGE_ALWAYS", "1")   # força publicar mesmo sem STRATEGOS_V2/editor
    monkeypatch.setenv("FORT_BADGE_SYNC", "1")     # caminho síncrono
    monkeypatch.setenv("FORTALEZA_API", "http://localhost:8765")
    monkeypatch.setenv("FORTALEZA_API_KEY", "test-key-xyz")

    monkeypatch.setattr(cli._urlreq, "urlopen", fake_urlopen)
    monkeypatch.setattr(cli.threading, "Thread", fail_thread)

    req_obj = {}  # sem contexto de editor
    out_obj = {"report": {"plan": {"mode": "PATCH", "attempts_to_green_est": 1.25}}}

    cli._maybe_post_strategos_badge_from_cli(req_obj, out_obj)

    assert calls["n"] == 1, "POST do badge não foi executado (caminho síncrono)"
    assert calls["url"].endswith("/strategos/badge")
    assert calls["headers"].get("Content-type") == "application/json"
    assert calls["headers"].get("X-api-key") == "test-key-xyz"
    payload = json.loads(calls["data"].decode("utf-8"))
    assert payload["mode"] == "PATCH"
    assert payload["attempts_to_green_est"] == 1.25
    assert "ts" in payload
