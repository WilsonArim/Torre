from __future__ import annotations
from pathlib import Path
import types

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from llm import engine as eng_mod

SHORT_PATCH = """<patch-info>{"generator":"B"}</patch-info>
```diff
--- a/README.md
+++ b/README.md
@@ -1 +1,2 @@
 A
+B
```
"""

LONG_PATCH = """<patch-info>{"generator":"A"}</patch-info>
```diff
--- a/README.md
+++ b/README.md
@@ -1,3 +1,6 @@
 A
-line
-here
+line
+here
+extra
```
"""

class DummyBackend:
    def __init__(self) -> None:
        pass
    def generate(self, system: str, user: str, profile: dict):
        # Se temperatura menor (PATCH), devolve patch mais LONGO; se maior (PATCH_B), devolve mais CURTO.
        t = float(profile.get("temperature", 0.1))
        if t <= 0.15:
            return LONG_PATCH, {"provider":"dummy","profile":"A"}
        else:
            return SHORT_PATCH, {"provider":"dummy","profile":"B"}

def test_engine_ab_picks_smaller(tmp_path: Path, monkeypatch):
    # monkeypatch o backend para não bater na rede
    monkeypatch.setenv("LLM_BACKEND", "openai_compat")
    def fake_backend_instance(name: str):
        return DummyBackend()
    monkeypatch.setattr(eng_mod, "_backend_instance", fake_backend_instance)

    out = eng_mod.run_inference(tmp_path, logs={"lint":"x"}, files={})
    assert "diff" in out and out["diff"].strip().startswith("--- a/README.md") or "```diff" in out["diff"]
    assert out["metrics"]["decode_winner"] in ("A","B")
    # SHORT_PATCH deve ganhar (menor tamanho) ⇒ "B"
    assert out["metrics"]["decode_winner"] == "B"
    assert "+B" in out["diff"]
