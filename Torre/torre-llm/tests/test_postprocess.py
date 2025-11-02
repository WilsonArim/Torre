from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from llm.postprocess import extract_patch

def _unified() -> str:
    return """<patch-info>{"generator":"TEST","ts":123}</patch-info>
```diff
--- a/README.md
+++ b/README.md
@@ -1 +1,2 @@
 Hello
+World
```
"""

def _raw_unified() -> str:
    return """--- a/README.md
+++ b/README.md
@@ -1 +1,2 @@
 Hello
+World
"""

def test_extract_with_codefence():
    diff, info = extract_patch(_unified())
    assert "+++ b/README.md" in diff
    assert "+World" in diff
    assert info.get("generator") == "TEST"

def test_extract_fallback_raw():
    diff, info = extract_patch(_raw_unified())
    assert diff.startswith("--- a/README.md")
    assert "+World" in diff
