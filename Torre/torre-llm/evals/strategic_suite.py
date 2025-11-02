from __future__ import annotations
import os, json, time, pathlib, tempfile, shutil
from typing import Dict, Any, List, Tuple, Callable
from .util_diff import extract_diff, looks_unified_diff, patch_size
from .util_project import (
    load_fixture_tree, build_import_graph, has_circular_import,
    detect_function_duplication, detect_unreachable_after_return,
    detect_hygiene_issues, detect_potential_new_cycle, read_tree_as_dict
)
from .cache_manager import CacheManager
from .log_optimizer import LogOptimizer
from .prompt_optimizer import PromptOptimizer

OK = True; FAIL = False

def _outdir() -> pathlib.Path:
    p = pathlib.Path(".fortaleza") / "evals"
    p.mkdir(parents=True, exist_ok=True)
    return p

def _now() -> str:
    import time as _t
    return _t.strftime("%Y%m%d-%H%M%S", _t.localtime())

def run_suite(dataset_path: str, providers: Dict[str, Callable], outdir: pathlib.Path) -> Dict[str, Any]:
    """Suite estratégica: avalia qualidade "militar/engenheiro/filósofo".
    Requer dataset JSONL com campos: {"fixture":"ts_minimal", "logs":{...},"objective":"..."}
    """
    # Inicializa otimizações
    cache_manager = CacheManager()
    log_optimizer = LogOptimizer()
    prompt_optimizer = PromptOptimizer()
    
    rows = []
    with open(dataset_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            rows.append(json.loads(line))
    
    ts = _now()
    report = {"ts": ts, "dataset": dataset_path, "providers": {}}
    
    for prov_name, fn in providers.items():
        if not fn: 
            continue
        stats = {"ok": 0, "count": 0, "sizes": [], "lat_ms": [], "violations": 0, "violations_samples": []}
        
        for i, ep in enumerate(rows, start=1):
            stats["count"] += 1
            fx = ep.get("fixture", "ts_minimal")
            fx_dir = pathlib.Path(__file__).parent / "fixtures" / fx
            
            # Tenta usar cache para fixture
            cache_key = f"fixture_{fx}"
            tree = cache_manager.get(cache_key)
            if tree is None:
                tree = load_fixture_tree(str(fx_dir))
                cache_manager.set(cache_key, tree, ttl=1800)  # 30 min
            
            import_graph = build_import_graph(tree)
            
            # Otimiza logs antes de fazer prompt
            original_logs = ep.get("logs", {})
            optimized_logs = log_optimizer.optimize_logs(original_logs)
            ep["logs"] = optimized_logs
            
            # Otimiza prompt completo
            prompt = prompt_optimizer.optimize_prompt(ep, tree)
            
            t0 = time.time()
            if prov_name == "our_llm_cli":
                # Prompt já é dict
                txt = fn(prompt)
            else:
                # Claude expects string
                txt = fn(json.dumps(prompt))
            lat = int((time.time() - t0) * 1000)
            stats["lat_ms"].append(lat)
            
            try:
                if isinstance(txt, dict):
                    diff_text = txt.get("diff", "")
                else:
                    diff_text = extract_diff(txt)
            except Exception as e:
                _mark_violation(stats, f"no-diff:{e}")
                continue
            
            # Guardrails "filósofo": formato/paths/single
            valid = looks_unified_diff(diff_text)
            if not valid:
                _mark_violation(stats, f"invalid-diff:format")
                continue
            
            size = patch_size(diff_text)[2]  # total
            stats["sizes"].append(size)
            
            # Tentativa de aplicar a um workspace temporário
            ws = tempfile.mkdtemp(prefix="fx-")
            try:
                # Materializa árvore
                for p, content in tree.items():
                    dst = pathlib.Path(ws) / p
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    dst.write_text(content, encoding="utf-8")
                
                # Aplica diff (simulado)
                # apply_ok = apply_unified_diff_if_available(ws, diff_text)
                
                # Recarrega árvore pós-patch para verificações
                after = read_tree_as_dict(ws)
                
                # Detectores "engenheiro"
                hy = detect_hygiene_issues(diff_text)
                if hy: 
                    _mark_violation(stats, "hygiene:" + ",".join(sorted(hy)))
                
                dup = detect_function_duplication(tree, after)
                if dup: 
                    _mark_violation(stats, "dup:" + ",".join(sorted(dup)))
                
                unr = detect_unreachable_after_return(diff_text)
                if unr: 
                    _mark_violation(stats, "unreachable:" + ",".join(sorted(unr)))
                
                # "militar": blast radius & ciclos
                if size > 1200: 
                    _mark_violation(stats, "blast-radius:diff-too-large")
                
                cyc_new = detect_potential_new_cycle(import_graph, diff_text)
                if cyc_new: 
                    _mark_violation(stats, "cycle:new-potential")
                
                cyc = has_circular_import(build_import_graph(after))
                if cyc: 
                    _mark_violation(stats, "cycle:actual")
                
                # sucesso se sem violações
                if stats["violations"] == 0:
                    stats["ok"] += 1
                    
            finally:
                shutil.rmtree(ws, ignore_errors=True)
        
        report["providers"][prov_name] = _aggregate(stats)
    
    # persistir
    out_json = _outdir() / f"bakeoff-{ts}.json"
    out_md = _outdir() / f"bakeoff-{ts}.md"
    out_json.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    out_md.write_text(_md_report(report), encoding="utf-8")
    return {"summary": report}

def _aggregate(stats: Dict[str, Any]) -> Dict[str, Any]:
    import statistics as S
    n = max(1, stats["count"])
    sizes = stats["sizes"] or [0]
    lat = stats["lat_ms"] or [0]
    return {
        "success_rate": round(100.0 * stats["ok"] / n, 2),
        "diff_size_mean": round(sum(sizes) / len(sizes), 2),
        "diff_size_p95": int(S.quantiles(sizes, n=20)[-1]) if len(sizes) >= 20 else max(sizes),
        "latency_p95_ms": int(S.quantiles(lat, n=20)[-1]) if len(lat) >= 20 else max(lat),
        "count": stats["count"],
        "violations_samples": stats.get("violations_samples", [])[:8]
    }

def _mark_violation(stats: Dict[str, Any], msg: str):
    stats["violations"] = stats.get("violations", 0) + 1
    arr = stats.setdefault("violations_samples", [])
    if len(arr) < 8: 
        arr.append(msg)

def _make_prompt(ep: Dict[str, Any], tree: Dict[str, str]) -> str:
    # Compacta o projeto em poucas entradas para o prompt
    files = {k: v for k, v in tree.items() if k.endswith((".ts", ".tsx"))}
    sample = dict(list(files.items())[:5])
    logs = ep.get("logs", {"lint": "TS2304: Cannot find name SettingsPage"})
    objective = ep.get("objective", "Corrigir erros e passar lint/tests sem aumentar blast radius.")
    
    # Formato compatível com nossa LLM
    payload = {"logs": logs, "files_before": sample}
    return json.dumps(payload, ensure_ascii=False)

def _md_report(rep: Dict[str, Any]) -> str:
    lines = []
    lines.append(f"## Bake-off Estratégico — {rep['ts']}\n")
    lines.append(f"Dataset: `{rep['dataset']}`\n")
    for p, met in rep["providers"].items():
        lines.append(f"### {p}\n")
        lines.append(f"- success_rate: **{met['success_rate']}%**")
        lines.append(f"- diff_size_mean/p95: {met['diff_size_mean']} / {met['diff_size_p95']}")
        lines.append(f"- latency_p95_ms: {met['latency_p95_ms']}")
        if met.get("violations_samples"):
            lines.append(f"- violations: {', '.join(met['violations_samples'])}")
        lines.append("")
    return "\n".join(lines)
