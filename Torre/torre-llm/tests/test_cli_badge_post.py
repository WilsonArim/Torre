import json
import types
import time

import pytest

import llm.cli as cli


class _DummyResp:
    def __enter__(self):
        return self
    def read(self):
        return b"{}"
    def __exit__(self, exc_type, exc, tb):
        return False


def test_badge_posts_when_always(monkeypatch):
    """
    Valida que o post é feito quando FORT_BADGE_ALWAYS=1,
    mesmo sem STRATEGOS_V2 e sem contexto de editor.
    """
    calls = {}

    def fake_urlopen(req, timeout=1.8):  # patches cli._urlreq.urlopen
        # Captura dados do Request
        calls["url"] = req.full_url
        calls["data"] = req.data
        calls["headers"] = dict(req.headers)
        calls["timeout"] = timeout
        return _DummyResp()

    class FakeThread:
        def __init__(self, target, args=(), kwargs=None, daemon=False):
            self.target = target
            self.args = args
            self.kwargs = kwargs or {}
            self.daemon = daemon
        def start(self):
            # Executa síncrono para teste determinístico
            self.target(*self.args, **self.kwargs)

    monkeypatch.setenv("FORT_BADGE_ALWAYS", "1")
    monkeypatch.delenv("STRATEGOS_V2", raising=False)  # mostra independência
    monkeypatch.setenv("FORTALEZA_API", "http://localhost:8765")
    monkeypatch.setenv("FORTALEZA_API_KEY", "test-key-123")

    monkeypatch.setattr(cli._urlreq, "urlopen", fake_urlopen)
    monkeypatch.setattr(cli.threading, "Thread", FakeThread)

    req_obj = {}  # sem contexto de editor
    out_obj = {
        "report": {
            "plan": {"mode": "PATCH", "attempts_to_green_est": 1.7}
        }
    }

    cli._maybe_post_strategos_badge_from_cli(req_obj, out_obj)

    assert "url" in calls, "badge POST não foi invocado"
    assert calls["url"].endswith("/strategos/badge")
    assert calls["headers"].get("Content-type") == "application/json"
    assert calls["headers"].get("X-api-key") == "test-key-123"

    payload = json.loads(calls["data"].decode("utf-8"))
    assert payload["mode"] == "PATCH"
    assert payload["attempts_to_green_est"] == 1.7
    assert "ts" in payload


def test_badge_opt_out(monkeypatch):
    """
    Valida que FORT_BADGE=0 desliga publicação.
    """
    monkeypatch.setenv("FORT_BADGE", "0")
    monkeypatch.setenv("STRATEGOS_V2", "1")
    monkeypatch.setenv("FORT_EDITOR", "1")

    called = {"n": 0}

    def fake_urlopen(req, timeout=1.8):
        called["n"] += 1
        return _DummyResp()

    class FakeThread:
        def __init__(self, target, args=(), kwargs=None, daemon=False):
            self.target = target
            self.args = args
            self.kwargs = kwargs or {}
            self.daemon = daemon
        def start(self):
            self.target(*self.args, **self.kwargs)

    import llm.cli as cli2
    monkeypatch.setattr(cli2._urlreq, "urlopen", fake_urlopen)
    monkeypatch.setattr(cli2.threading, "Thread", FakeThread)

    req_obj = {"context": {"ide": "vscode"}}
    out_obj = {"metrics": {"strategos": {"mode": "ADVISORY", "attempts_to_green_est": 2.0}}}

    cli2._maybe_post_strategos_badge_from_cli(req_obj, out_obj)
    assert called["n"] == 0, "badge deveria estar desativado por FORT_BADGE=0"
