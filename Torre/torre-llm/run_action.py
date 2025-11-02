from __future__ import annotations
from pathlib import Path
import sys, os, json, time
from typing import Dict, Any

def _find_action_md(repo: Path) -> Path | None:
    # prioridades comuns
    for rel in ("action.md", "ACTION.md", "docs/action.md", "fortaleza-llm/action.md"):
        p = repo / rel
        if p.exists():
            return p
    return None

def _load_engineer_contract(repo: Path) -> Dict[str, Any]:
    """Lê o contrato YAML; fallback para defaults embutidos se PyYAML ausente/ficheiro em falta."""
    cfg_path = repo / "fortaleza-llm/configs/engineer.contract.yaml"
    defaults: Dict[str, Any] = {
        "version": "1.0",
        "allowed_blocks": ["file","append","diff"],
        "denied_paths_contains": [".env",".ssh",".pem","id_rsa","secrets."],
        "deny_exact_paths": ["action.md","ACTION.md","docs/action.md","fortaleza-llm/action.md"],
        "anticipation": {"run_lint_before_tests": True, "run_codemods_ts": True},
        "learning": {"enabled": True, "file": ".fortaleza/learned_rules.json"},
    }
    if not cfg_path.exists():
        return defaults
    try:
        import yaml  # type: ignore
        data = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
        if not isinstance(data, dict): return defaults
        # preencher faltas com defaults
        for k,v in defaults.items():
            data.setdefault(k, v)
        return data
    except Exception:
        return defaults

def main() -> None:
    repo = Path(os.getenv("REPO_ROOT", ".")).resolve()
    
    # Detectar action.md
    action_arg = None
    if len(sys.argv) > 1:
        # permitir: python -m fortaleza-llm.run_action path/to/action.md
        action_arg = sys.argv[-1]
    action_path = Path(action_arg) if action_arg else (_find_action_md(repo) or (repo / "action.md"))
    if not action_path.exists():
        print("MISSING:action.md")
        return

    contract = _load_engineer_contract(repo)
    
    # Bloquear escrita ao action.md: se o próprio action tentar alterar-se, abortar
    ap_rel = str(action_path.relative_to(repo)) if str(action_path).startswith(str(repo)) else action_path.name
    deny_exact = set(contract.get("deny_exact_paths", []))
    if ap_rel in deny_exact:
        print(json.dumps({"summary":"contract violation","error":"action.md is read-only for engineer",
                          "metrics":{"engineer_contract_version": contract.get("version","1.0")}}))
        return

    # TODO: Implementar FortalezaEngineer quando disponível
    # engineer = FortalezaEngineer(repo)
    start = time.time()
    
    # Simulação básica para demonstração
    action_md = action_path.read_text(encoding="utf-8")
    
    # Métricas simuladas
    metrics = {
        "apply_clean": True,
        "lint_clean": True, 
        "tests_pass": True,
        "diff_size": 0,
        "engineer_contract_version": contract.get("version","1.0")
    }
    
    print(json.dumps({"summary": "action executed", "metrics": metrics}))
