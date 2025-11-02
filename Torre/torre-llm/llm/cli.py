from __future__ import annotations
import sys, json, os
import time
import threading
from pathlib import Path
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from urllib import request as _urlreq
try:
    import jsonschema
except Exception:
    jsonschema = None

# Contracts
from pathlib import Path as _P
_CONTRACTS_DIR = _P(__file__).resolve().parent.parent / "contracts"
def _load_schema(name: str):
    p = _CONTRACTS_DIR / name
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None
_SCHEMA_IN = _load_schema("input.schema.json")
_SCHEMA_OUT = _load_schema("output.schema.json")

def _validate_json(payload: dict, schema: dict | None, where: str):
    if not schema or not jsonschema:
        return
    jsonschema.validate(payload, schema)  # may raise

def _utc_iso():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")

def _estimate_tokens(s: str) -> int:
    return max(0, int(len(s) / 4))

# ---- Memória Episódica (opcional, segura) ----
try:
    from llm.memory.episodic import EpisodicMemory
except Exception:
    EpisodicMemory = None

# ---- Strategos v2 (opcional, segura) ----
try:
    from llm.strategos.scorer_v2 import StrategosV2Graph
    from llm.reverse.codemap import CodeMap
except Exception:
    StrategosV2Graph = None
    CodeMap = None

from llm.execution.reranker import Reranker  # novo
try:
    from evals.strategos_v2 import StrategosV2  # se existir
except Exception:
    StrategosV2 = None
try:
    from evals.learning_system import LearningSystem  # se existir (Fase 7)
except Exception:
    LearningSystem = None
from llm.forensics.impact_analyzer import analyze_diff  # novo (Fase 10.1)
from llm.rag.canon import pick_lenses, lens_report         # novo (Fase 10.2)
from llm.optimization.cost_optimizer import choose_route   # novo (Fase 10.3)

# F20 providers
try:
    from llm.providers.router import ProvidersRouter
    from llm.providers.base import ProviderRequest
    _HAS_PROVIDERS = True
except Exception:
    _HAS_PROVIDERS = False

def _maybe_attach_strategos_plan(resp: dict, req: dict):
    """
    Opcional: anexa plano Strategos v2 ao output quando STRATEGOS_V2=1.
    Não falha a CLI se faltarem dependências.
    """
    if os.getenv("STRATEGOS_V2", "0") != "1":
        return
    try:
        if not StrategosV2Graph:
            return
        try:
            codemap = CodeMap().build(".") if CodeMap else {"nodes": [], "edges": []}
        except Exception:
            codemap = {"nodes": [], "edges": []}
        logs = req.get("logs") or {}
        files = (req.get("files") or {})
        # episódios (fase 14) se existir
        try:
            episodes = EpisodicMemory()._load_episodes() if EpisodicMemory else []
        except Exception:
            episodes = []
        plan = StrategosV2Graph().plan(codemap, logs, files, episodes, top_k=6)
        (resp.setdefault("metrics", {}))["strategos"] = {
            "mode": plan.get("mode"),
            "nodes_considered": plan.get("nodes_considered"),
            "attempts_to_green_est": len(plan.get("steps", [])) // 4,  # heurística leve
            "ttg_delta_est": -0.2 if plan.get("mode") == "PATCH" else 0.0,
        }
        resp.setdefault("report", {})["plan"] = plan
        _maybe_post_strategos_badge(resp)
        _maybe_post_strategos_event(resp)
    except Exception:
        # não quebra a CLI
        pass

def _detect_editor_mode(req_obj: dict) -> bool:
    """
    Heurística leve para saber se a CLI foi acionada a partir do editor.
    - FORT_EDITOR=1 (forçar)
    - req_obj.context.ide (ex.: "vscode" / "cursor")
    - req_obj.meta.ide / req_obj.source == "editor"
    """
    if os.getenv("FORT_EDITOR") == "1":
        return True
    try:
        ctx = (req_obj or {}).get("context") or {}
        meta = (req_obj or {}).get("meta") or {}
        if isinstance(ctx, dict) and ctx.get("ide"):
            return True
        if meta.get("ide") or (req_obj or {}).get("source") == "editor":
            return True
    except Exception:
        pass
    return False


def _extract_strategos_badge_payload(out_obj: dict) -> dict:
    """
    Extrai {mode, attempts_to_green_est, ts} de out_obj.
    Procura primeiro em report.plan, depois em metrics.strategos.
    """
    mode = None
    a2g = None
    try:
        plan = (out_obj or {}).get("report", {}).get("plan", {}) or {}
        mode = plan.get("mode") or mode
        a2g = plan.get("attempts_to_green_est") if a2g is None else a2g
    except Exception:
        pass
    try:
        strat = (out_obj or {}).get("metrics", {}).get("strategos", {}) or {}
        mode = strat.get("mode") or mode
        a2g = strat.get("attempts_to_green_est") if a2g is None else a2g
    except Exception:
        pass
    # valor seguro padrão
    mode = mode or "ADVISORY"
    badge = {
        "mode": mode,
        "attempts_to_green_est": a2g if isinstance(a2g, (int, float)) else None,
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    return badge


def _post_strategos_badge(badge: dict, api_url: str, api_key: str = None, timeout: float = 1.8) -> None:
    """
    POST /strategos/badge com timeout curto e falha silenciosa.
    Não levanta exceções para não quebrar a CLI.
    """
    try:
        url = api_url.rstrip("/") + "/strategos/badge"
        data = json.dumps(badge).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["x-api-key"] = api_key
        req = _urlreq.Request(url, data=data, headers=headers, method="POST")
        with _urlreq.urlopen(req, timeout=timeout) as resp:
            # melhor esforço; ignoramos o corpo
            _ = resp.read()
    except (URLError, HTTPError, TimeoutError, Exception):
        # falha silenciosa
        return


def _maybe_post_strategos_badge_from_cli(req_obj: dict, out_obj: dict) -> None:
    """
    Publica o badge automaticamente quando a CLI é chamada pelo editor.
    Respeita:
      - STRATEGOS_V2=1  (somente publica se o Strategos v2 estiver habilitado)
      - FORT_BADGE=0    (opt-out explícito)
      - FORT_BADGE_ALWAYS=1 (força publicação mesmo fora do editor e sem STRATEGOS_V2)
      - FORT_BADGE_SYNC=1   (executa o POST de forma síncrona — útil para testes/debug)
    """
    try:
        if os.getenv("FORT_BADGE", "1") == "0":
            return
        always = os.getenv("FORT_BADGE_ALWAYS") == "1"
        if not always:
            if os.getenv("STRATEGOS_V2", "0") != "1":
                return
            if not _detect_editor_mode(req_obj):
                return
        api_url = os.getenv("FORTALEZA_API", "http://localhost:8765")
        api_key = os.getenv("FORTALEZA_API_KEY")
        badge = _extract_strategos_badge_payload(out_obj)
        # Execução síncrona (debug) ou assíncrona (default)
        if os.getenv("FORT_BADGE_SYNC") == "1":
            _post_strategos_badge(badge, api_url, api_key, 1.8)
        else:
            # evitar bloquear a CLI: disparo "fire-and-forget" em thread curta
            t = threading.Thread(
                target=_post_strategos_badge,
                args=(badge, api_url, api_key, 1.8),
                daemon=True,
            )
            t.start()
    except Exception:
        return


def _maybe_post_strategos_badge(out_json):
    """POST opcional para o servidor expor mini badge na UI."""
    try:
        if os.getenv("STRATEGOS_V2", "0") != "1":
            return
        api = os.getenv("FORTALEZA_API", "http://localhost:8765")
        if not api:
            return
        mode = (out_json.get("metrics", {}).get("strategos", {}) or {}).get("mode", "ADVICE")
        a2g = (out_json.get("metrics", {}).get("strategos", {}) or {}).get("attempts_to_green_est")
        payload = {
            "mode": mode,
            "attempts_to_green_est": a2g,
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        }
        body = json.dumps(payload)
        if isinstance(body, (bytes, bytearray)):  # paranoia: nunca .encode() duas vezes
            raw = body
        else:
            raw = body.encode("utf-8")
        req = Request(f"{api}/strategos/badge", data=raw,
                      headers={"Content-Type": "application/json"}, method="POST")
        urlopen(req, timeout=2)  # fire-and-forget (sem quebrar a CLI)
    except URLError:
        pass
    except Exception:
        # não propagamos erro de telemetria
        pass

def _maybe_post_strategos_event(out_json):
    """Posta evento para hover card (opcional)"""
    try:
        api = os.getenv("FORTALEZA_API", "http://localhost:8765")
        req = Request(
            f"{api}/strategos/events",
            data=json.dumps({
                "mode": out_json.get("metrics", {}).get("strategos", {}).get("mode", "NONE"),
                "attempts_to_green_est": out_json.get("metrics", {}).get("strategos", {}).get("attempts_to_green_est", 0),
                "ts": out_json.get("trace_id", ""),
            }).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urlopen(req, timeout=5)
    except Exception:
        pass

def _maybe_apply_with_rollback(out_obj: dict):
    """Fase 17: Rollback on Red (opt-in)"""
    if not os.getenv("FORT_APPLY"):
        return out_obj
    api = os.getenv("FORTALEZA_API", "http://localhost:8765")
    workspace = os.getenv("FORT_WORKSPACE", ".")
    diff = out_obj.get("diff")
    if not diff:
        out_obj.setdefault("meta", {})["apply"] = {"skipped": True, "reason": "no-diff"}
        return out_obj
    try:
        req = Request(
            f"{api}/ops/apply",
            data=json.dumps({"workspace": workspace, "diff": diff}).encode("utf-8"),
            headers={"Content-Type":"application/json", **({"x-api-key": os.getenv("FORTALEZA_API_KEY")} if os.getenv("FORTALEZA_API_KEY") else {})},
            method="POST",
        )
        with urlopen(req, timeout=10) as r:
            body = r.read()
            try:
                res = json.loads(body.decode("utf-8"))
            except Exception:
                res = {"ok": False, "raw": body[:200].decode("utf-8","ignore")}
    except Exception as e:
        res = {"ok": False, "error": str(e)}
    out_obj.setdefault("meta", {})["apply"] = res
    return out_obj
    """POST opcional dos últimos planos (para hover card na UI)."""
    try:
        if os.getenv("STRATEGOS_V2", "0") != "1":
            return
        api = os.getenv("FORTALEZA_API", "http://localhost:8765")
        if not api:
            return
        plan = (out_json.get("report", {}) or {}).get("plan", {}) or {}
        mode = (out_json.get("metrics", {}).get("strategos", {}) or {}).get("mode", plan.get("mode", "ADVICE"))
        a2g = (out_json.get("metrics", {}).get("strategos", {}) or {}).get("attempts_to_green_est")
        steps = plan.get("steps") or []
        top = []
        for s in steps[:3]:
            stage = s.get("stage")
            target = s.get("target")
            score = s.get("score")
            if stage and target:
                item = {"stage": stage, "target": target}
                if isinstance(score, (int, float)):
                    item["score"] = float(score)
                top.append(item)
        payload = {
            "mode": mode,
            "attempts_to_green_est": a2g,
            "steps": top,
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        }
        body = json.dumps(payload)
        raw = body if isinstance(body, (bytes, bytearray)) else body.encode("utf-8")
        req = Request(f"{api}/strategos/events", data=raw,
                      headers={"Content-Type": "application/json"}, method="POST")
        urlopen(req, timeout=2)
    except URLError:
        pass
    except Exception:
        pass

def main() -> None:
    """
    CLI oficial da LLM: lê JSON de stdin com {"logs":{}, "files":{}} e escreve {"diff","metrics","patch_info"}.
    Uso:
      echo '{"logs":{"lint":"..."},"files":{}}' | python -m fortaleza-llm.llm.cli
    """
    try:
        raw = sys.stdin.read()
        body = json.loads(raw or "{}")
    except Exception:
        print(json.dumps({"error":"Invalid JSON on stdin"}))
        sys.exit(1)

    from .engine import run_inference
    repo = Path(os.getenv("REPO_ROOT",".")).resolve()
    logs = body.get("logs") or {}
    files = body.get("files") or {}
    
    # === F20: Providers + Router (opt-in via env) ===========================
    use_providers = os.getenv("PROVIDERS_V1", "0") == "1" and _HAS_PROVIDERS
    providers_meta = {}
    provider_candidates = []
    if use_providers:
        try:
            router = ProvidersRouter(root=".")
            decision = router.decide(logs, files)
            providers_meta["router_decision"] = decision
            preq = ProviderRequest(logs=logs, files=files, meta=body.get("meta") or {})
            provider_candidates = router.generate_candidates(preq, decision)
            providers_meta["candidates"] = [
                {
                    "provider": c.provider,
                    "tokens_in": c.tokens_in,
                    "tokens_out": c.tokens_out,
                    "latency_ms": c.latency_ms,
                } for c in provider_candidates
            ]
        except Exception as e:
            providers_meta["error"] = f"{type(e).__name__}: {e}"
    
    # (Fase 10.3) Otimizador custo/latência — decide modelo/janela e comprime logs
    if os.getenv("LLM_OPTIMIZE","1")=="1":
        route = choose_route(logs, files)
        # expõe decisão (sem depender do backend, mas respeita quem lê LLM_MODEL)
        os.environ["LLM_MODEL"]=route["model"]
        logs = route["compressed_logs"]

    # Antes de gerar: aplicar priors seguros (kits) se habilitado
    if os.getenv("FORT_MEM", "1") != "0" and EpisodicMemory:
        try:
            em = EpisodicMemory()
            req = {"files": files}
            req = em.apply_priors(req, logs, context={})
            files = req.get("files", files)
            mem_metrics = em.metrics()
        except Exception as _:
            pass

    # Rerank agora ON por padrão; opt-out via LLM_RERANK=0
    rerank_flag = str(os.getenv("LLM_RERANK", "")).lower()
    enable_rerank = rerank_flag not in ("0", "false", "off", "no")
    
    # Rerank (F13) — se tivermos candidatos por provedor, usamos eles
    selected_provider = None
    if provider_candidates:
        diffs = [c.diff for c in provider_candidates]
        try:
            from llm.rerank.execution_reranker import ExecutionReranker
            rr = ExecutionReranker()
            rr_res = rr.run(req.get("workspace","default"), diffs, k=min(3, len(diffs)))
            idx = rr_res.get("selected_index", 0)
            selected_provider = provider_candidates[idx].provider if 0 <= idx < len(provider_candidates) else provider_candidates[0].provider
            providers_meta["selected"] = {
                "provider": selected_provider,
                "index": idx,
                "diff_size": rr_res.get("winner",{}).get("diff_size"),
                "ttg_ms": rr_res.get("winner",{}).get("ttg_ms"),
            }
            # injeta diff vencedor no fluxo downstream (como se fosse um único candidato)
            body.setdefault("meta", {})["provider_winner"] = selected_provider
            body.setdefault("meta", {})["provider_candidates_count"] = len(provider_candidates)
            # opcional: expor direto no topo para toolings antigos
            body["diff"] = diffs[idx] if 0 <= idx < len(diffs) else diffs[0]
        except Exception as e:
            providers_meta["rerank_error"] = f"{type(e).__name__}: {e}"
            selected_provider = provider_candidates[0].provider
            body["diff"] = provider_candidates[0].diff
    
    if enable_rerank:
        # --- Fase 13: Rerank n-best por execução (agora ON por padrão; opt-out via LLM_RERANK=0) ---
        try:
            # Extrai candidatos de forma tolerante a formatos
            candidates = []
            
            # Gerar candidatos usando o sistema existente
            strat = StrategosV2() if StrategosV2 else None
            learn = LearningSystem() if LearningSystem else None
            rer = Reranker(strategos_v2=strat, learning_system=learn)

            # Geradores de candidatos:
            # 1) Base (engine padrão)
            def gen_base():
                o = run_inference(repo, logs=logs, files=files)
                return ("base", o.get("diff", ""))
            # 2) Lesson-assisted (se LearningSystem existir)
            def gen_lesson():
                hints = None
                try:
                    if learn and hasattr(learn, "rewrite_prompt"):
                        hints = learn.rewrite_prompt({"logs": logs, "files": files})
                except Exception:
                    hints = None
                o = run_inference(repo, logs=logs, files=files)  # simplificação: engine lê hints do contexto se suportado
                return ("lesson", o.get("diff", ""))
            # 3) Synthesis/Stub (opcional; fallback para base se não houver gerador próprio)
            def gen_synth():
                o = run_inference(repo, logs=logs, files=files)  # em produção: chamar sintetizador dedicado
                return ("synth", o.get("diff", ""))

            result = rer.run(logs, files, [gen_base, gen_lesson, gen_synth])
            
            # Extrair diffs dos candidatos para o execution reranker
            if isinstance(result.get("candidates"), list):
                for c in result["candidates"]:
                    if isinstance(c, dict) and isinstance(c.get("diff"), str):
                        candidates.append(c["diff"])
                    elif isinstance(c, str):
                        candidates.append(c)
            
            # Se não há candidatos, usar o diff vencedor
            if not candidates and isinstance(result.get("winner", {}).get("diff"), str):
                candidates = [result["winner"]["diff"]]
            
            # Se ainda não há candidatos, usar o diff do resultado final
            if not candidates and isinstance(result.get("winner", {}).get("diff"), str):
                candidates = [result["winner"]["diff"]]
            elif not candidates and isinstance(result.get("diff"), str):
                candidates = [result["diff"]]

            if candidates:
                # Preferir workspace do pedido; cair para "default"
                ws = body.get("workspace") or os.getenv("FORTALEZA_WORKSPACE", "default")
                # Reranker via HTTP com fallback local
                from llm.rerank.client import rerank as _rr

                rr = _rr(ws, candidates, k=min(3, len(candidates)))
                # Se houver vencedor, substituir diff e anexar relatório
                if rr.get("selected_index") is not None:
                    sel = int(rr["selected_index"])
                    if 0 <= sel < len(candidates):
                        result["winner"]["diff"] = candidates[sel]
                
                # Sempre anexa telemetria de rerank
                result.setdefault("metrics", {})["execution_rerank"] = rr
            else:
                # Se não há candidatos, ainda executar o reranker com o diff final
                ws = body.get("workspace") or os.getenv("FORTALEZA_WORKSPACE", "default")
                from llm.rerank.client import rerank as _rr
                
                final_diff = result.get("winner", {}).get("diff") or result.get("diff", "")
                if final_diff:
                    rr = _rr(ws, [final_diff], k=1)
                    result.setdefault("metrics", {})["execution_rerank"] = rr
            
            # Emite o vencedor (mantendo contrato)
            out = {
                "diff": result["winner"]["diff"],
                "metrics": {
                    "rerank": True,
                    "winner": result["winner"]["name"],
                    "candidates": result["candidates"],
                    "strategos": bool(result["strategos"]),
                    "memory_used": bool(result["memory"]),
                    "optimizer": os.environ.get("LLM_MODEL",""),
                },
                "patch_info": {"mode": "RERANK"},
            }
            
            # Métricas/telemetria F20
            if use_providers:
                out["metrics"].setdefault("providers", {})
                out["metrics"]["providers"].update(providers_meta)
                # traço mínimo (F16 estendido): provider vencedor e tokens estimados
                if provider_candidates:
                    win = next((c for c in provider_candidates if c.provider == selected_provider), None)
                    if win:
                        out["metrics"].setdefault("trace", {})
                        out["metrics"]["trace"].update({
                            "provider": win.provider,
                            "tokens_in": win.tokens_in,
                            "tokens_out": win.tokens_out,
                        })
            # Adicionar métricas de memória se disponíveis
            if 'mem_metrics' in locals():
                out["metrics"]["memory"] = mem_metrics
            # (Fase 10.1) Forense de impacto + (Fase 10.2) Lentes do CANON
            try:
                forensic = analyze_diff(logs, files, out["diff"])
                lenses = pick_lenses(logs, out["diff"])
                out["metrics"]["forensics"]=forensic["summary"]
                out["metrics"]["lenses"]=lens_report(lenses)
            except Exception:
                pass
            # (Fase 15) Strategos v2 plan se habilitado
            _maybe_attach_strategos_plan(out, body)
            
            # publicar badge Strategos automaticamente quando invocado pelo editor
            _maybe_post_strategos_badge_from_cli(body, out)
            
            print(json.dumps(out, ensure_ascii=False))
        except Exception as _e:  # hard-fail nunca; log leve em métricas
            try:
                # Fallback para o comportamento original se algo der errado
                out = run_inference(repo, logs=logs, files=files)
                out.setdefault("metrics", {})["rerank_error"] = str(_e)
                print(json.dumps(out, ensure_ascii=False))
            except Exception:
                pass
    else:
        out = run_inference(repo, logs=logs, files=files)  # mantém compat
        # Adicionar métricas de memória se disponíveis
        if 'mem_metrics' in locals():
            out.setdefault("metrics", {})["memory"] = mem_metrics
        
        # Métricas/telemetria F20 (também no fluxo simples)
        if use_providers:
            out.setdefault("metrics", {})
            out["metrics"].setdefault("providers", {})
            out["metrics"]["providers"].update(providers_meta)
            # traço mínimo (F16 estendido): provider vencedor e tokens estimados
            if provider_candidates:
                win = next((c for c in provider_candidates if c.provider == selected_provider), None)
                if win:
                    out["metrics"].setdefault("trace", {})
                    out["metrics"]["trace"].update({
                        "provider": win.provider,
                        "tokens_in": win.tokens_in,
                        "tokens_out": win.tokens_out,
                    })
        # Forense + Lentes também no fluxo simples
        try:
            forensic = analyze_diff(logs, files, out.get("diff",""))
            lenses = pick_lenses(logs, out.get("diff",""))
            out.setdefault("metrics",{})["forensics"]=forensic["summary"]
            out.setdefault("metrics",{})["lenses"]=lens_report(lenses)
        except Exception:
            pass
        # (Fase 15) Strategos v2 plan se habilitado
        _maybe_attach_strategos_plan(out, body)
        # (Fase 17) Rollback on Red (opt-in)
        out = _maybe_apply_with_rollback(out)
        
        # publicar badge Strategos automaticamente quando invocado pelo editor
        _maybe_post_strategos_badge_from_cli(body, out)
        
        print(json.dumps(out, ensure_ascii=False))

if __name__ == "__main__":
    main()
