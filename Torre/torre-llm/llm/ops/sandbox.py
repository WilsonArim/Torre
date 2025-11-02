import os, subprocess, tempfile, shutil, sys, signal, json
from typing import List, Dict, Optional, Tuple
try:
    import resource  # POSIX
except Exception:
    resource = None

def _preexec(cpu_seconds:int, mem_mb:int, nproc:int, nofile:int):
    def _apply():
        try:
            os.setsid()
        except Exception:
            pass
        if resource:
            # CPU
            try: resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
            except Exception: pass
            # memória (address space) ~ MB -> bytes
            limit = mem_mb * 1024 * 1024
            for r in ("RLIMIT_AS","RLIMIT_DATA","RLIMIT_RSS"):
                rl = getattr(resource, r, None)
                if rl is None: continue
                try: resource.setrlimit(rl, (limit, limit))
                except Exception: pass
            # processos/arquivos
            try: resource.setrlimit(resource.RLIMIT_NPROC, (nproc, nproc))
            except Exception: pass
            try: resource.setrlimit(resource.RLIMIT_NOFILE, (nofile, nofile))
            except Exception: pass
    return _apply

def _fake_bin_dir() -> str:
    """
    Cria um diretório com shims que bloqueiam ferramentas de rede comuns.
    É um 'no-network' best-effort que funciona em CI/container.
    """
    d = tempfile.mkdtemp(prefix="fort_no_net_")
    script = "#!/usr/bin/env bash\necho 'network disabled by sandbox' >&2; exit 137\n"
    for name in ("curl","wget","git","pip","npm","pnpm","yarn","uv","apt","apk"):
        p = os.path.join(d, name)
        with open(p,"w") as f: f.write(script)
        os.chmod(p, 0o755)
    return d

def run_in_sandbox(
    cmd: List[str],
    cwd: Optional[str]=None,
    env: Optional[Dict[str,str]]=None,
    timeout_s:int=60,
    cpu_seconds:int=15,
    mem_mb:int=1024,
    nproc:int=256,
    nofile:int=1024,
    no_network:bool=True,
) -> Tuple[int,str,str]:
    env2 = dict(os.environ)
    if env: env2.update({k:str(v) for k,v in env.items()})
    env2.pop("HTTP_PROXY", None); env2.pop("HTTPS_PROXY", None)
    env2["FORT_NO_NET"] = "1" if no_network else "0"
    # Shims anti-rede primeiro no PATH
    clean = None
    if no_network:
        fake = _fake_bin_dir()
        clean = fake
        env2["PATH"] = f"{fake}:{env2.get('PATH','')}"
    try:
        p = subprocess.Popen(
            cmd,
            cwd=cwd,
            env=env2,
            preexec_fn=_preexec(cpu_seconds, mem_mb, nproc, nofile),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            out, err = p.communicate(timeout=timeout_s)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(p.pid, signal.SIGKILL)
            except Exception:
                p.kill()
            return (124, "", "timeout")
        return (p.returncode, out or "", err or "")
    finally:
        if clean and os.path.isdir(clean):
            shutil.rmtree(clean, ignore_errors=True)
