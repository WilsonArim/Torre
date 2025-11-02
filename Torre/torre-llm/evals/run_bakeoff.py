from __future__ import annotations
import os, sys, json, time
from pathlib import Path
from statistics import mean
from typing import Dict, Any, List
try:
    from .providers import call_our_llm_cli, call_claude, call_openai_compat, make_prompt_from_episode
    from .util_diff import extract_diff, looks_unified_diff, patch_size
    from .fortaleza_api import validate_diff
    from .strategic_suite import run_suite as run_suite_strategic
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from evals.providers import call_our_llm_cli, call_claude, call_openai_compat, make_prompt_from_episode
    from evals.util_diff import extract_diff, looks_unified_diff, patch_size
    from evals.fortaleza_api import validate_diff
    from evals.strategic_suite import run_suite as run_suite_strategic

DEF_DATASET = "fortaleza-llm/evals/datasets/bakeoff.sample.jsonl"

def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            rows.append(json.loads(line))
    return rows

def now_id() -> str:
    return time.strftime("%Y%m%d-%H%M%S", time.localtime())

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default=DEF_DATASET)
    ap.add_argument("--suite", default="classic", choices=["classic", "strategic"])
    args = ap.parse_args()
    
    ds_path = Path(args.dataset)
    if not ds_path.exists():
        print(f"ERROR: dataset not found: {ds_path}", file=sys.stderr)
        sys.exit(2)
    episodes = read_jsonl(ds_path)
    if not episodes:
        print("ERROR: empty dataset", file=sys.stderr)
        sys.exit(2)

    # Suite estratégica
    if args.suite == "strategic":
        providers = {
            "our_llm_cli": call_our_llm_cli,
            "claude": call_claude if os.getenv("ANTHROPIC_API_KEY") else None
        }
        outdir = Path(".fortaleza/evals")
        outdir.mkdir(parents=True, exist_ok=True)
        res = run_suite_strategic(str(ds_path), providers, outdir)
        print(json.dumps(res["summary"], indent=2))
        return

    # Providers ativos
    use_claude = bool(os.getenv("ANTHROPIC_API_KEY"))
    use_oa_compat = bool(os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_MODEL"))
    # Nossa LLM (CLI) sempre ativa

    results: Dict[str, Any] = {
        "id": now_id(),
        "dataset": str(ds_path),
        "providers": {
            "our_llm_cli": True,
            "claude": use_claude,
            "openai_compat": use_oa_compat
        },
        "episodes_total": len(episodes),
        "runs": {}
    }

    def run_for_provider(name: str):
        runs = []
        for ep in episodes:
            inp = {"logs": ep.get("logs", {}), "files": ep.get("files_before", {})}
            try:
                if name == "our_llm_cli":
                    out = call_our_llm_cli(inp)
                    diff = out.get("diff","")
                    dur = out.get("duration_ms", 0)
                elif name == "claude":
                    prompt = make_prompt_from_episode(ep)
                    out = call_claude(prompt)
                    diff = out.get("diff","")
                    dur = out.get("duration_ms", 0)
                elif name == "openai_compat":
                    prompt = make_prompt_from_episode(ep)
                    out = call_openai_compat(prompt)
                    diff = out.get("diff","")
                    dur = out.get("duration_ms", 0)
                else:
                    raise RuntimeError(f"unknown provider {name}")
                valid_fmt = looks_unified_diff(diff)
                adds, removes, total = patch_size(diff) if valid_fmt else (0,0,0)
                fort = validate_diff(diff)  # pode ser skipped
                success = bool(valid_fmt and (fort.get("ok") or fort.get("skipped")))
            except Exception as e:
                diff = ""
                dur = 0
                valid_fmt = False
                adds=removes=total=0
                success = False
                out = {"error": str(e)}
                fort = {"ok": False, "error": str(e)}
            runs.append({
                "episode_id": ep.get("id"),
                "success": success,
                "valid_unified": valid_fmt,
                "adds": adds, "removes": removes, "diff_size": total,
                "duration_ms": dur,
                "fortaleza_validation": fort,
                "raw_hint": (out if isinstance(out, dict) else {"raw": str(out)})  # guarda só pista, não a resposta completa
            })
        results["runs"][name] = runs

    # Executa
    run_for_provider("our_llm_cli")
    if use_claude:
        run_for_provider("claude")
    if use_oa_compat:
        run_for_provider("openai_compat")

    # Agregados
    def agg(name: str):
        runs = results["runs"].get(name, [])
        if not runs: 
            return {}
        succ = [1 for r in runs if r["success"]]
        sizes = [r["diff_size"] for r in runs if r["diff_size"]>0]
        durs = [r["duration_ms"] for r in runs if r["duration_ms"]>0]
        def p95(xs: List[int]) -> int:
            if not xs: return 0
            xs = sorted(xs); k = int(0.95*(len(xs)-1))
            return xs[k]
        return {
            "success_rate": round(100.0 * (sum(succ)/len(runs)), 2),
            "diff_size_mean": round(mean(sizes), 2) if sizes else 0.0,
            "diff_size_p95": p95(sizes),
            "latency_p95_ms": p95(durs),
            "count": len(runs)
        }
    results["summary"] = {name: agg(name) for name in results["runs"].keys()}

    # Persistir
    outdir = Path(".fortaleza/evals"); outdir.mkdir(parents=True, exist_ok=True)
    base = outdir / f"bakeoff-{results['id']}"
    (base.with_suffix(".json")).write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    # Markdown rápido
    md = [f"# Bake-off {results['id']}", f"- Dataset: `{results['dataset']}`", ""]
    for name, s in results["summary"].items():
        md.append(f"## {name}")
        md.append(f"- success_rate: **{s.get('success_rate',0)}%**")
        md.append(f"- diff_size_mean/p95: {s.get('diff_size_mean',0)} / {s.get('diff_size_p95',0)}")
        md.append(f"- latency_p95_ms: {s.get('latency_p95_ms',0)}")
        md.append("")
    (base.with_suffix(".md")).write_text("\n".join(md), encoding="utf-8")
    print(json.dumps(results["summary"], indent=2))

if __name__ == "__main__":
    main()
