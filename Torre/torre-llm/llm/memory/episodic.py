from __future__ import annotations
import json, re, os, hashlib
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime, timezone

# Limites defensivos
MAX_FIELD_LEN = 2000           # cada string sanitizada
MAX_LINE_BYTES = 32 * 1024     # cada linha JSONL
MAX_FILE_BYTES = 5 * 1024 * 1024  # tamanho p/ rotacionar episodes.jsonl

def _truncate(s: str, lim: int = MAX_FIELD_LEN) -> str:
    if not isinstance(s, str):
        s = str(s)
    return s if len(s) <= lim else s[:lim] + "…"

def _rotate_if_needed(path: str):
    try:
        if os.path.exists(path) and os.path.getsize(path) >= MAX_FILE_BYTES:
            ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
            dst = f"{path.rsplit('.',1)[0]}-{ts}.jsonl"
            os.replace(path, dst)
    except Exception:
        # rotação best-effort; não impede execução
        pass

# Ficheiros
MEM_DIR = Path(".fortaleza/memory")
EP_FILE = MEM_DIR / "episodes.jsonl"
RULES_FILE = MEM_DIR / "rules.json"
META_FILE = MEM_DIR / "meta.json"

PII_RE = re.compile(r"([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})", re.I)
SECRET_RE = re.compile(r"(sk-[A-Za-z0-9_\-]{16,}|ghp_[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9\-]{10,}|AIza[0-9A-Za-z\-_]{35})")
ABS_PATH_RE = re.compile(r"(^\/|^[A-Za-z]:\\)")

def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

def _repo_hash() -> str:
    root = os.getcwd()
    return hashlib.sha1(root.encode()).hexdigest()[:12]

def _safe_rel(path: str) -> str:
    path = path.replace("\\", "/")
    if ABS_PATH_RE.search(path):  # força relativo
        return Path(path).name
    return path.lstrip("./")

def _sanitize(s: str) -> str:
    s = PII_RE.sub("[redacted-email]", s)
    s = SECRET_RE.sub("[redacted-secret]", s)
    return s[:2000]  # limite defensivo

@dataclass
class Episode:
    ts: str
    repo: str
    file: str | None
    err_code: str | None
    err_msg: str | None
    toolchain: str | None
    action: str  # "patch" | "advice" | "codemod" | "prior"
    outcome: str # "green" | "fail" | "unknown"
    extras: Dict[str, Any]

    @staticmethod
    def build(raw: Dict[str, Any]) -> "Episode":
        return Episode(
            ts=raw.get("ts") or _utc_iso(),
            repo=raw.get("repo") or _repo_hash(),
            file=_safe_rel(str(raw.get("file"))) if raw.get("file") else None,
            err_code=str(raw.get("err_code") or "").upper()[:16] or None,
            err_msg=_sanitize(str(raw.get("err_msg") or "")) or None,
            toolchain=(raw.get("toolchain") or None),
            action=str(raw.get("action") or "patch"),
            outcome=str(raw.get("outcome") or "unknown"),
            extras={k:v for k,v in raw.items() if k not in {"ts","repo","file","err_code","err_msg","toolchain","action","outcome"}},
        )

class EpisodicMemory:
    def __init__(self, mem_dir: Path | None = None):
        self.mem_dir = mem_dir or MEM_DIR
        self.mem_dir.mkdir(parents=True, exist_ok=True)
        if not RULES_FILE.exists():
            RULES_FILE.write_text("[]", encoding="utf-8")
        if not META_FILE.exists():
            META_FILE.write_text(json.dumps({"avoidance_saves":0}, indent=2), encoding="utf-8")

    # ---------- persistência ----------
    def append(self, ep: Episode) -> None:
        data = asdict(ep)
        # truncar campos grandes
        for k, v in list(data.items()):
            if isinstance(v, str):
                data[k] = _truncate(v)
        line = json.dumps(data, ensure_ascii=False)
        if len(line.encode("utf-8")) > MAX_LINE_BYTES:
            # se ainda excede, mantém campos essenciais
            slim = {k: data.get(k) for k in ("ts", "repo", "file", "err_code", "err_msg", "toolchain", "action", "outcome")}
            line = json.dumps(slim, ensure_ascii=False)
        self.mem_dir.mkdir(parents=True, exist_ok=True)
        _rotate_if_needed(str(EP_FILE))
        with EP_FILE.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    def _load_episodes(self, limit:int=5000) -> List[Dict[str,Any]]:
        if not EP_FILE.exists(): return []
        out: List[Dict[str,Any]] = []
        with EP_FILE.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    out.append(json.loads(line))
                except: pass
        return out[-limit:]

    def _load_rules(self) -> List[Dict[str,Any]]:
        try:
            return json.loads(RULES_FILE.read_text(encoding="utf-8"))
        except:
            return []

    def _save_rules(self, rules: List[Dict[str,Any]]) -> None:
        RULES_FILE.write_text(json.dumps(rules, indent=2, ensure_ascii=False), encoding="utf-8")

    def _load_meta(self) -> Dict[str,Any]:
        try:
            return json.loads(META_FILE.read_text(encoding="utf-8"))
        except:
            return {"avoidance_saves":0}

    def _save_meta(self, meta: Dict[str,Any]) -> None:
        META_FILE.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

    # ---------- promoção de regras ----------
    def promote_rules(self, n:int=3) -> Tuple[int,int]:
        """Promove regras if-this-then-that após N≥3 sucessos sem regressão."""
        eps = self._load_episodes()
        buckets: Dict[str, List[Dict[str,Any]]] = {}
        for e in eps:
            key = "|".join(filter(None, [
                e.get("repo"), e.get("err_code"),
                (e.get("file") or "").split("/")[0] or None,
                e.get("toolchain") or None
            ]))
            buckets.setdefault(key, []).append(e)
        rules = self._load_rules()
        added=0; kept=0
        for key, lst in buckets.items():
            succ = [x for x in lst if x.get("outcome")=="green"]
            fail = [x for x in lst if x.get("outcome")=="fail"]
            if len(succ) >= n and len(fail)==0:
                if not any(r.get("key")==key for r in rules):
                    rules.append({"key":key, "confidence":0.8, "hits":0, "regressions":0,
                                  "policy":"apply_priors", "created_at":_utc_iso()})
                    added+=1
                else:
                    kept+=1
            # se houver regressão, despromove:
            if fail:
                rules = [r for r in rules if r.get("key")!=key]
        self._save_rules(rules)
        return added, kept

    # ---------- aplicação de priors seguros ----------
    def apply_priors(self, request: Dict[str,Any], logs: Dict[str,Any], context: Dict[str,Any] | None=None) -> Dict[str,Any]:
        """
        Aplica correções *antes* da geração. Área segura: kits assets/jsx/node/tests (idempotentes).
        """
        try:
            from evals.codemods.ts_ambient_kits import ensure_ambient_kit
        except Exception:
            return request
        msg_raw = " ".join([str(v) for v in (logs or {}).values()])
        msg = msg_raw.lower()
        files = request.setdefault("files", {})
        applied = []
        # heurísticas rápidas e seguras
        if ("cannot find module" in msg and (".css" in msg or ".svg" in msg or ".png" in msg or ".json" in msg)):
            _, files, ch = ensure_ambient_kit(files, "assets")
            if ch: applied.append("kit:assets")
        if ("jsx element implicitly has type" in msg) or ("intrinsic elements" in msg):
            _, files, ch = ensure_ambient_kit(files, "jsx")
            if ch: applied.append("kit:jsx")
        if ("cannot find name 'process'" in msg) or ("cannot find name 'buffer'" in msg):
            _, files, ch = ensure_ambient_kit(files, "node")
            if ch: applied.append("kit:node")
        if ("vitest" in msg) or ("@types/vitest" in msg):
            _, files, ch = ensure_ambient_kit(files, "tests-vitest")
            if ch: applied.append("kit:tests-vitest")
        if ("jest" in msg) or ("@types/jest" in msg):
            _, files, ch = ensure_ambient_kit(files, "tests-jest")
            if ch: applied.append("kit:tests-jest")
        if applied:
            meta = request.setdefault("meta", {})
            mem = self._load_meta()
            mem["avoidance_saves"] = int(mem.get("avoidance_saves",0)) + 1
            self._save_meta(mem)
            meta["priors_applied"] = applied
        return request

    # ---------- métricas ----------
    def metrics(self) -> Dict[str,Any]:
        eps = self._load_episodes()
        rules = self._load_rules()
        mem = self._load_meta()
        # taxa de repetição: falhas com mesmo err_code+bucket após 2+ ocorrências
        seen=set(); repeats=0; total=max(1,len(eps))
        for e in eps:
            k = (e.get("err_code"), (e.get("file") or "").split("/")[0])
            if k in seen and e.get("outcome")=="fail":
                repeats += 1
            seen.add(k)
        return {
            "repeat_error_rate": round(100*repeats/total, 2),
            "rules_promoted": len(rules),
            "rules_hit_rate": round(100*sum(r.get("hits",0) for r in rules)/max(1,len(eps)), 2),
            "avoidance_saves": int(mem.get("avoidance_saves",0)),
        }
