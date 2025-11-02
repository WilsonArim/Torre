import os, json, subprocess, tempfile, time
from pathlib import Path
from typing import Dict, Any, Tuple, List
from .sandbox import run_in_sandbox

DEFAULT_GATES = {
    "lint": ["bash","-lc","npm run -s lint || true; echo DONE"],
    "types": ["bash","-lc","npm run -s typecheck || true; echo DONE"],
    "tests": ["bash","-lc","npm test -s -- --watch=false || true; echo DONE"],
    "build": ["bash","-lc","npm run -s build || true; echo DONE"],
}

def _git(workspace:str, args:List[str]) -> Tuple[int,str,str]:
    # Git básico (init, config, add, commit) pode rodar sem sandbox
    # Apenas operações de rede (fetch, push, pull) precisam de sandbox
    if any(network_op in args for network_op in ["fetch", "push", "pull", "clone"]):
        return run_in_sandbox(["git","-C",workspace] + args, timeout_s=30, no_network=True)
    else:
        import subprocess
        result = subprocess.run(["git","-C",workspace] + args, capture_output=True, text=True)
        return (result.returncode, result.stdout, result.stderr)

def _locked(workspace:str) -> Path:
    p = Path(workspace)/".fortaleza"/"locks"
    p.mkdir(parents=True, exist_ok=True)
    return p/"rollback.lock"

def ensure_not_locked(workspace:str):
    lf = _locked(workspace)
    if lf.exists():
        raise RuntimeError(f"workspace locked by rollback: {lf}")

def apply_with_rollback(
    workspace:str,
    diff:str,
    gates:Dict[str,Any]=None,
    quotas:Dict[str,int]=None,
) -> Dict[str,Any]:
    ensure_not_locked(workspace)
    gates = gates or DEFAULT_GATES
    quotas = quotas or {"cpu_seconds": 20, "mem_mb": 2048, "timeout_s": 120}
    # HEAD atual
    rc,out,err = _git(workspace, ["rev-parse","--short","HEAD"])
    if rc!=0: raise RuntimeError(f"git error: {err}")
    head = out.strip()
    # checar e aplicar diff
    rc,_,err = _git(workspace, ["apply","--check","-"])
    if rc!=0: return {"ok": False, "stage":"apply-check", "error": err}
    rc,_,err = run_in_sandbox(["git","-C",workspace,"apply","-"], timeout_s=30, no_network=True, mem_mb=256)
    if rc!=0: return {"ok": False, "stage":"apply", "error": err}
    _git(workspace, ["add","-A"])
    _git(workspace, ["commit","-m","[fortaleza] apply candidate"])
    rc,out,_ = _git(workspace, ["rev-parse","--short","HEAD"])
    new_head = out.strip()
    # executar gates no sandbox
    results = {}
    any_red = False
    for name, cmd in gates.items():
        rc, out, err = run_in_sandbox(
            cmd, cwd=workspace,
            timeout_s=quotas.get("timeout_s",120),
            cpu_seconds=quotas.get("cpu_seconds",20),
            mem_mb=quotas.get("mem_mb",2048),
            no_network=True,
        )
        passed = (rc==0)
        # heurística: se comando devolve 0 mas contem 'FAIL' no stderr/stdout → falha
        text = (out+"\n"+err).lower()
        if "fail" in text or "error" in text and name!="build":
            passed = False
        results[name] = {"rc": rc, "passed": passed, "out": out[-4000:], "err": err[-4000:]}
        if not passed: any_red = True
        # short-circuit: se build vermelho, para cedo
        if not passed and name in ("build","types"): break
    if any_red:
        # rollback + lock
        _git(workspace, ["revert","--no-edit", new_head])
        lock = _locked(workspace)
        lock.write_text(json.dumps({"ts": int(time.time()), "head": head, "reverted": new_head, "reason":"gate-failed"}))
        return {"ok": False, "rolled_back": True, "lock": str(lock), "head": head, "reverted": new_head, "gates": results}
    return {"ok": True, "rolled_back": False, "head": new_head, "gates": results}
