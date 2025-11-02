# sanity_check_phase17.py
import os, tempfile, json, subprocess, textwrap
from pathlib import Path

from llm.ops.sandbox import run_in_sandbox
from llm.ops.guard_apply import apply_with_rollback, ensure_not_locked, _locked
from llm.guard.secret_scan import scan_diff_for_secrets

GREEN = "✅"
RED = "❌"

def header(t): print(f"\n=== {t} ===")

def test_sandbox_no_network():
    header("Sandbox: no-network + quotas")
    rc,out,err = run_in_sandbox(["curl","https://example.com"], timeout_s=5, cpu_seconds=1, mem_mb=128, no_network=True)
    assert rc != 0 and "network disabled" in (err or "").lower(), f"{RED} curl deveria falhar no sandbox"
    print(f"{GREEN} rede bloqueada (curl interceptado)")

    rc,out,err = run_in_sandbox(["python3","-c","print(1)"], timeout_s=5, cpu_seconds=1, mem_mb=128)
    assert rc == 0 and out.strip()=="1", f"{RED} python simples deveria rodar"
    print(f"{GREEN} quotas básicas ok (CPU/Mem/Timeout)")

def _git(cwd, *args):
    return subprocess.run(["git","-C",cwd, *args], capture_output=True, text=True)

def _git_sandbox(cwd, *args):
    """Git executado no sandbox (sem rede)"""
    return run_in_sandbox(["git","-C",cwd] + list(args), timeout_s=30, no_network=True)

def _make_repo():
    temp = tempfile.TemporaryDirectory(prefix="fort17_")
    root = temp.name
    _git(root, "init", "-q")
    _git(root, "config", "user.email", "dev@local")
    _git(root, "config", "user.name", "Dev")
    (Path(root)/".fortaleza").mkdir(exist_ok=True)
    # arquivo inicial
    p = Path(root)/"app.txt"
    p.write_text("hello\n", encoding="utf-8")
    _git(root, "add", "app.txt")
    _git(root, "commit", "-q", "-m", "init")
    return temp, root

def _diff_add_line():
    before = ["hello\n"]
    after  = ["hello\n", "added\n"]
    import difflib
    return "".join(difflib.unified_diff(
        before, after,
        fromfile="a/app.txt",
        tofile="b/app.txt",
        lineterm=""
    ))

def test_waf_secret_scan():
    header("WAF: secret scan")
    diff = textwrap.dedent("""\
        --- a/a
        +++ b/a
        @@ -0,0 +1 @@
        +const api_key = "sk-123456789012345678901234567890";
    """)
    viol = scan_diff_for_secrets(diff)
    assert len(viol) >= 1, f"{RED} secret scanner deveria detectar token"
    print(f"{GREEN} secret scanner detectou {len(viol)} ocorrência(s)")

def test_apply_with_rollback_and_lock():
    header("Apply → gates → Rollback + lock")
    temp, repo = _make_repo()
    try:
        diff = _diff_add_line()

        # Gates: força falha logo no começo (types)
        gates = {
            "lint":  ["bash","-lc","echo LINT OK; exit 0"],
            "types": ["bash","-lc","echo FAIL types; exit 1"],  # <- vermelho
            "tests": ["bash","-lc","echo TESTS (não será executado); exit 0"],
            "build": ["bash","-lc","echo BUILD (não será executado); exit 0"],
        }

        res = apply_with_rollback(repo, diff, gates=gates, quotas={"cpu_seconds":5,"mem_mb":256,"timeout_s":10})
        assert res.get("ok") is False and res.get("rolled_back") is True, f"{RED} deveria fazer rollback"
        lock_file = _locked(repo)
        assert lock_file.exists(), f"{RED} lock não foi criado"
        meta = json.loads(lock_file.read_text())
        assert meta.get("reason")=="gate-failed", f"{RED} motivo do lock incorreto"
        print(f"{GREEN} rollback executado e lock criado → {lock_file}")

        # Verifica que lock impede nova aplicação
        blocked = False
        try:
            ensure_not_locked(repo)
        except Exception:
            blocked = True
        assert blocked, f"{RED} ensure_not_locked deveria bloquear"
        print(f"{GREEN} lock ativo bloqueando novas aplicações")

    finally:
        # liberação do tmp
        temp.cleanup()

if __name__ == "__main__":
    test_sandbox_no_network()
    test_waf_secret_scan()
    test_apply_with_rollback_and_lock()
    print(f"\n{GREEN} Sanity Phase 17: TUDO OK")
