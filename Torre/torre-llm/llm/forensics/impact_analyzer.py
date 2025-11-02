from __future__ import annotations
import re
from typing import Dict, Any, List, Tuple

# Cobertura mais robusta para chaves comuns (sem guardar valores reais)
_SECRET_RE = re.compile(
    r"("
    r"sk-[A-Za-z0-9_\-]{16,}"                          # OpenAI-like
    r"|ghp_[A-Za-z0-9]{20,}"                           # GitHub PAT
    r"|xox[baprs]-[A-Za-z0-9\-]{10,}"                  # Slack tokens
    r"|AIza[0-9A-Za-z\-_]{35}"                         # Google API
    r"|(?:api|token|secret|key)[-_]?[=:]\s*['\"][A-Za-z0-9_\-]{16,}['\"]"  # genérico
    r")",
    re.I,
)
_HDR_OLD = re.compile(r"^--- a/(.+)$")
_HDR_NEW = re.compile(r"^\+\+\+ b/(.+)$")

def _parse_diff(diff:str)->List[Dict[str,Any]]:
    files=[]; cur=None; adds=rems=0
    old=new=None
    for ln in diff.splitlines():
        m1=_HDR_OLD.match(ln); m2=_HDR_NEW.match(ln)
        if m1:
            old=m1.group(1); continue
        if m2:
            # fecha anterior
            if cur:
                cur["adds"]=adds; cur["removes"]=rems; files.append(cur)
                adds=rems=0
            new=m2.group(1)
            cur={"path":new or old or "", "adds":0, "removes":0}
            continue
        if ln.startswith("+") and not ln.startswith("+++"): adds+=1
        elif ln.startswith("-") and not ln.startswith("---"): rems+=1
    if cur:
        cur["adds"]=adds; cur["removes"]=rems; files.append(cur)
    return files

def _layer_for(path:str)->str:
    p=path.lower()
    if p.startswith(("src/ui","ui/","app/","pages/","components/")): return "UI"
    if p.startswith(("src/domain","domain/","core/")): return "DOMAIN"
    if p.startswith(("src/service","services/","api/","server/")): return "SERVICE"
    if p.startswith(("infra/","ops/","deploy/","config/",".github/")): return "INFRA"
    if p.startswith(("tests/","__tests__/")) or p.endswith((".spec.ts",".test.ts",".spec.py",".test.py")): return "TEST"
    return "OTHER"

def _ext(path:str)->str:
    for ext in (".tsx",".ts",".jsx",".js",".py",".json",".yml",".yaml",".md",".toml",".lock",".cfg",".ini"):
        if path.endswith(ext): return ext
    return ""

def _secret_hits(texts:List[str])->int:
    c=0
    for t in texts:
        c+=len(list(_SECRET_RE.finditer(t)))
    return c

def analyze_diff(logs:Dict[str,str], files_before:Dict[str,str], diff:str)->Dict[str,Any]:
    """
    Forense de impacto: ficheiros tocados, camadas, risco e sinais (segredos/hotspots/dup).
    """
    touched=_parse_diff(diff)
    layers_count={}
    total_adds=total_rems=0
    for f in touched:
        f["ext"]=_ext(f["path"])
        f["layer"]=_layer_for(f["path"])
        layers_count[f["layer"]]=layers_count.get(f["layer"],0)+1
        total_adds+=f["adds"]; total_rems+=f["removes"]

    # Sinais rápidos
    secrets=_secret_hits([diff])
    big_patch = (total_adds+total_rems)>300
    ui_touches = sum(1 for f in touched if f["layer"]=="UI")
    infra_touches = sum(1 for f in touched if f["layer"]=="INFRA")

    # risco (0-100) simples e explicável
    risk=0
    if secrets>0: risk+=50
    if big_patch: risk+=20
    if infra_touches>0: risk+=15
    if ui_touches>0: risk+=5

    return {
        "summary": {
            "files_touched": len(touched),
            "lines": {"add": total_adds, "rem": total_rems, "total": total_adds+total_rems},
            "layers": layers_count,
            "secrets_found": secrets,
            "risk_score": min(100, risk),
        },
        "files": touched,
        "signals": {
            "big_patch": big_patch,
            "ui_touches": ui_touches,
            "infra_touches": infra_touches,
        }
    }
