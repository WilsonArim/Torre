from __future__ import annotations
from pathlib import Path
from typing import Dict, Any
import os, json

def _json_response(body: Dict[str, Any], status: int = 200):
    return status, {"Content-Type":"application/json"}, json.dumps(body)

def _run_core(body: Dict[str, Any]) -> Dict[str, Any]:
    from .engine import run_inference
    repo = Path(os.getenv("REPO_ROOT",".")).resolve()
    logs = body.get("logs") or {}
    files = body.get("files") or {}
    out = run_inference(repo, logs=logs, files=files)
    return out

# FastAPI se disponível; fallback para WSGI micro
def create_app():
    try:
        import os, time
        from fastapi import FastAPI, APIRouter, Body, HTTPException, Query, Request, Depends, Response
        from fastapi.middleware.cors import CORSMiddleware
        from pydantic import BaseModel, Field, validator
        from typing import Any, Dict, Optional, List
        from pathlib import Path
        from datetime import datetime, timezone, timedelta
        from collections import deque
        from ipaddress import ip_address
        import json, uuid
        try:
            import jsonschema  # optional but preferred
        except Exception:  # pragma: no cover
            jsonschema = None

        from llm.guard.secret_scan import scan_diff_for_secrets
        from llm.rerank.execution_reranker import ExecutionReranker

        # ⬇️ PATCH: Fase 11 — expor POST /research/vanguard/brief
        try:
            from .research.vanguard_brief import generate_brief, validate_brief
            from .research.admin_gate import propose_to_canon
        except Exception:
            # Mantém o servidor funcional mesmo que os módulos não estejam presentes durante build parcial
            generate_brief = None   # type: ignore
            validate_brief = None   # type: ignore
            propose_to_canon = None # type: ignore

        # ⬇️ PATCH: Fase 14 — memória episódica
        try:
            from .memory.episodic import EpisodicMemory
        except Exception:
            EpisodicMemory = None

        # ⬇️ PATCH: Fase 17 — Rollback on Red + Sandbox
        try:
            from .ops.guard_apply import apply_with_rollback, ensure_not_locked
            from .guard.secret_scan import scan_diff_for_secrets
        except Exception:
            apply_with_rollback = None
            ensure_not_locked = None
            scan_diff_for_secrets = None

        # ⬇️ PATCH: Fase 15 — Strategos v2 com grafo
        try:
            from .reverse.codemap import CodeMap                 # F08 (reutilizado)
            from .strategos.scorer_v2 import StrategosV2Graph    # F15
        except Exception:
            CodeMap = None
            StrategosV2Graph = None

        # --- Strategos badge (volatile, para UI) -------------------------------------
        _STRATEGOS_EVENTS: List[dict] = []  # ring buffer em memória (máx 50)
        
        # ---------------- Security & QoS helpers (rate limit + auth) -----------------
        _RATE_BUCKETS: Dict[str, Dict[str, Any]] = {}  # key=f"{ip}|{route}", value={"win":int,"count":int}
        
        # ========= Contracts & Tracing =========
        _CONTRACTS_DIR = Path(__file__).resolve().parent.parent / "contracts"
        _TRACE_DIR = Path(".fortaleza/trace")
        _TRACE_DIR.mkdir(parents=True, exist_ok=True)

        def _utc_iso():
            return datetime.now(timezone.utc).isoformat(timespec="milliseconds")

        def _new_trace_id() -> str:
            return str(uuid.uuid4())

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

        def _validate_json(payload: dict, schema: dict | None, *, where: str):
            if not schema or not jsonschema:
                return  # soft-fallback if jsonschema not installed
            try:
                jsonschema.validate(payload, schema)  # type: ignore
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Schema validation failed ({where}): {e}")

        def _rotate_trace_files(max_files: int = 7):
            files = sorted(_TRACE_DIR.glob("trace-*.jsonl"))
            while len(files) > max_files:
                old = files.pop(0)
                try:
                    old.unlink(missing_ok=True)
                except Exception:
                    break

        def _trace_log(record: dict):
            try:
                fn = _TRACE_DIR / f"trace-{datetime.now(timezone.utc).strftime('%Y%m%d')}.jsonl"
                line = json.dumps(record, ensure_ascii=False) + "\n"
                fn.parent.mkdir(parents=True, exist_ok=True)
                with fn.open("a", encoding="utf-8") as f:
                    f.write(line)
                if fn.stat().st_size > 5 * 1024 * 1024:
                    _rotate_trace_files()
            except Exception:
                pass

        def _estimate_tokens(s: str) -> int:
            # Rough heuristic: 1 token ~= 4 chars
            return max(0, int(len(s) / 4))

        def _summarize_sizes(obj) -> int:
            try:
                return len(json.dumps(obj, ensure_ascii=False))
            except Exception:
                return 0

        router = APIRouter()

        class StrategosBadgeIn(BaseModel):
            mode: str = "ADVICE"   # "PATCH" | "ADVICE" | "NONE"
            attempts_to_green_est: float | None = None
            ts: str | None = None

        @router.get("/strategos/badge")
        def get_strategos_badge(request: Request):
            badge = dict(request.app.state.STRATEGOS_BADGE)
            badge["recent_posts_1h"] = _recent_badge_posts_1h()
            return badge

        @router.post("/strategos/badge")
        def set_strategos_badge(badge: StrategosBadgeIn, request: Request):
            request.app.state.STRATEGOS_BADGE = {**badge.dict(), "ts": _utc_iso()}
            # registra o POST para a janela de 1h
            request.app.state.STRATEGOS_BADGE_POST_TIMES.append(datetime.now(timezone.utc))
            return {"ok": True, "recent_posts_1h": _recent_badge_posts_1h(), "badge": request.app.state.STRATEGOS_BADGE}

        # --- Strategos eventos (para hover card) -------------------------------------
        def _client_ip(req: Request) -> str:
            # confia no IP direto; se atrás de proxy, pode aceitar X-Forwarded-For em setups controlados
            return (req.client.host if req.client else "0.0.0.0") or "0.0.0.0"

        def rate_limit(limit: int, per_seconds: int = 60):
            def _dep(req: Request):
                now = int(time.time())
                win = now // per_seconds
                ip = _client_ip(req)
                key = f"{ip}|{req.url.path}"
                entry = _RATE_BUCKETS.get(key)
                if not entry or entry["win"] != win:
                    _RATE_BUCKETS[key] = {"win": win, "count": 1}
                    return
                entry["count"] += 1
                if entry["count"] > limit:
                    raise HTTPException(status_code=429, detail="Rate limit exceeded")
            return _dep

        class StrategosEventIn(BaseModel):
            mode: str = "ADVICE"   # "PATCH" | "ADVICE" | "NONE"
            attempts_to_green_est: Optional[float] = None
            ts: Optional[str] = None
            steps: Optional[List[Dict[str, Any]]] = None  # [{stage,target,score?}, ...]

        @router.get("/strategos/events", dependencies=[Depends(rate_limit(120, 60))])
        def get_strategos_events(limit: int = Query(3, ge=1, le=50)):
            # retorna mais recentes primeiro
            if not _STRATEGOS_EVENTS:
                return {"events": []}
            sl = _STRATEGOS_EVENTS[-limit:]
            return {"events": list(reversed(sl))}

        @router.post("/strategos/events", dependencies=[Depends(rate_limit(60, 60))])
        def post_strategos_event(ev: StrategosEventIn):
            data = ev.dict()
            if not data.get("ts"):
                data["ts"] = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
            _STRATEGOS_EVENTS.append(data)
            # ring buffer máx 50
            overflow = len(_STRATEGOS_EVENTS) - 50
            if overflow > 0:
                del _STRATEGOS_EVENTS[0:overflow]
            return {"ok": True}

        def require_api_key(req: Request):
            """Se FORTALEZA_API_KEY estiver setada, exige 'x-api-key' ou 'Authorization: Bearer' com a mesma chave.
            Caso contrário, permite livremente para 127.0.0.1/::1 (modo dev)."""
            want = os.getenv("FORTALEZA_API_KEY", "").strip()
            if not want:
                # dev: só aceita chamadas locais
                host = _client_ip(req)
                try:
                    ip = ip_address(host)
                    if ip.is_loopback:
                        return
                except Exception:
                    pass
                # sem chave e fora de loopback → permitir mas marcar como 403 leve
                # (poderia bloquear; aqui mantemos compat com setups atuais)
                return
            got = req.headers.get("x-api-key") or ""
            if not got:
                auth = req.headers.get("authorization") or ""
                if auth.lower().startswith("bearer "):
                    got = auth.split(" ", 1)[1].strip()
            if got != want:
                raise HTTPException(status_code=401, detail="Unauthorized")

        # ---------------- Inputs: validações leves p/ endpoints críticos -------------
        class PlanIn(BaseModel):
            logs: Dict[str, str] = Field(default_factory=dict)
            files: Dict[str, str] = Field(default_factory=dict)
            class Config:
                extra = "ignore"
            @validator("logs")
            def _v_logs(cls, v):
                if len(v) > 32:
                    raise ValueError("too many log fields")
                for k, s in v.items():
                    if not isinstance(s, str) or len(s) > 8000:
                        raise ValueError("log entry too large")
                return v
            @validator("files")
            def _v_files(cls, v):
                if len(v) > 32:
                    raise ValueError("too many files")
                total = 0
                for p, s in v.items():
                    if not isinstance(s, str):
                        raise ValueError("file must be string")
                    if len(p) > 256 or ".." in p or p.startswith(("/", "\\")):
                        raise ValueError("invalid path")
                    ln = len(s)
                    if ln > 200_000:
                        raise ValueError("file too large")
                    total += ln
                if total > 800_000:
                    raise ValueError("payload too large")
                return v

        # ===========================
        # Fase 12: guard & audit APIs
        # ===========================
        class SecretScanRequest(BaseModel):
            diff: str

        @router.post("/guard/secret-scan")
        def api_secret_scan(req: SecretScanRequest) -> Dict[str, Any]:
            violations = scan_diff_for_secrets(req.diff or "")
            return {
                "allowed": len(violations) == 0,
                "count": len(violations),
                "violations": violations,
            }

        class AuditLog(BaseModel):
            action: str
            actor: Optional[str] = None
            trace_id: Optional[str] = None
            metadata: Dict[str, Any] = {}

        @router.post("/audit/log")
        def api_audit_log(entry: AuditLog) -> Dict[str, Any]:
            audit_dir = Path(".fortaleza/audit")
            audit_dir.mkdir(parents=True, exist_ok=True)
            rec = {
                "ts": datetime.utcnow().isoformat(timespec="seconds") + "Z",
                **entry.model_dump(),
            }
            with (audit_dir / "log.jsonl").open("a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            return {"ok": True, "stored": True}

        # ===========================
        # Fase 17: Rollback on Red + Sandbox & Quotas
        # ===========================
        class ApplyIn(BaseModel):
            workspace: str
            diff: str
            quotas: Optional[Dict[str,int]] = None

        @router.post("/ops/apply", dependencies=[Depends(rate_limit(20, 60)), Depends(require_api_key)])
        def ops_apply(payload: ApplyIn):
            # validações rígidas (WAF)
            if not payload.workspace or not payload.diff:
                raise HTTPException(400, "workspace and diff required")
            if len(payload.diff) > 800_000:
                raise HTTPException(413, "diff too large")
            viol = scan_diff_for_secrets(payload.diff)
            if viol:
                raise HTTPException(400, f"secret-like patterns detected: {len(viol)}")
            # lock check
            try:
                ensure_not_locked(payload.workspace)
            except Exception as e:
                raise HTTPException(423, str(e))
            try:
                res = apply_with_rollback(payload.workspace, payload.diff, quotas=payload.quotas or {})
                return {"ok": bool(res.get('ok')), **res}
            except Exception as e:
                raise HTTPException(500, str(e))

        # ===========================
        # Fase 13: reranker n-best
        # ===========================
        class RerankRequest(BaseModel):
            workspace: str = "default"
            candidates: List[str]
            k: int = 3

        @router.post(
            "/rerank/execute",
            dependencies=[Depends(rate_limit(30, 60)), Depends(require_api_key)]
        )
        def api_rerank_execute(req: RerankRequest) -> Dict[str, Any]:
            if not req.candidates:
                raise HTTPException(status_code=400, detail="No candidates provided")
            rr = ExecutionReranker()
            result = rr.run(req.workspace, req.candidates, k=req.k)
            # Política: se nenhum passou, devolve só relatório (UI/CLI entra em ADVISORY-mode)
            return {
                "ok": True,
                "selected_index": result.get("selected_index"),
                "winner": result.get("winner"),
                "candidates": result.get("candidates"),
                "discard_reasons": result.get("discard_reasons"),
                "metrics": {
                    "avg_candidates": result.get("avg_candidates"),
                    # ganchos para telemetria futura:
                    "n_best_win_rate": None,
                    "selection_ttg_ms": result.get("winner", {}).get("ttg_ms") if result.get("winner") else None,
                    "selected_diff_size": result.get("winner", {}).get("diff_size") if result.get("winner") else None,
                },
            }

        def _build_app() -> FastAPI:
            app = FastAPI()
            # CORS de desenvolvimento (em produção, trocar por allow_origins específicos)
            app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_methods=["*"],
                allow_headers=["*"],
            )
            app.include_router(router)
            
            # Estado global do app
            app.state.STRATEGOS_BADGE = {"mode": "NONE", "attempts_to_green_est": None, "ttg_delta_est_ms": None, "meta": {}}
            app.state.KPI_BADGE = {"golden_sr": None, "repeat_error_rate": None, "requests_today": None, "ts": None}
            # Histórico de POSTs do badge (timestamps UTC) para métrica de 1h
            app.state.STRATEGOS_BADGE_POST_TIMES = deque(maxlen=10000)

            def _recent_badge_posts_1h() -> int:
                """Prune e conta POSTs do /strategos/badge feitos na última hora."""
                dq = app.state.STRATEGOS_BADGE_POST_TIMES
                if dq is None:
                    return 0
                now = datetime.now(timezone.utc)
                cutoff = now - timedelta(hours=1)
                while dq and dq[0] < cutoff:
                    dq.popleft()
                return len(dq)

            @app.get("/health")
            def _health():
                return {"ok": True}

            # ---------- F14: Memória Episódica ----------
            @app.get("/memory/metrics")
            def memory_metrics():
                """
                Retorna métricas da memória episódica + regras promovidas (read-only).
                Formato:
                {
                  "metrics": { repeat_error_rate, rules_promoted, rules_hit_rate, avoidance_saves },
                  "rules": [{ key, confidence, hits, regressions, policy, created_at }]
                }
                """
                if not EpisodicMemory:
                    return {"metrics": {}, "rules": []}
                em = EpisodicMemory()
                metrics = em.metrics()
                try:
                    rules = em._load_rules()  # leitura segura (somente leitura)
                except Exception:
                    rules = []
                return {"metrics": metrics, "rules": rules}

            # ---------- F14 (opcional): promover regras a partir dos episódios ----------
            @app.post("/memory/promote", dependencies=[Depends(rate_limit(10, 60)), Depends(require_api_key)])
            def memory_promote():
                """
                Força reprocessamento de episódios -> regras promovidas.
                Retorna { ok, promoted, rules }.
                """
                if not EpisodicMemory:
                    return {"ok": False, "promoted": 0, "rules": []}
                em = EpisodicMemory()
                # em.promote_rules() pode retornar lista, contagem ou dict — normalizamos:
                try:
                    res = em.promote_rules()  # método read-only sobre episodes.jsonl -> rules.json
                except Exception as e:
                    return {"ok": False, "error": str(e), "promoted": 0, "rules": []}
                try:
                    if isinstance(res, dict):
                        promoted = int(res.get("promoted", 0))
                        rules = res.get("rules") or em._load_rules()
                    elif isinstance(res, list):
                        promoted = len(res)
                        rules = res
                    else:
                        promoted = int(res or 0)
                        rules = em._load_rules()
                except Exception:
                    promoted = int(res or 0)
                    rules = []
                return {"ok": True, "promoted": promoted, "rules": rules}

            # ------------------------ F15: Grafo leve (resumo) -------------------------
            @app.get("/graph/summary")
            def graph_summary():
                """
                Retorna contagem de nós/arestas e top-5 por centralidade aproximada.
                Usa CodeMap (fase 8). Fallback gracioso se indisponível.
                """
                if not CodeMap:
                    return {"nodes": 0, "edges": 0, "top": []}
                cm = CodeMap()
                g = cm.build(".")  # raiz do workspace (padrão)
                nodes = g.get("nodes") or []
                edges = g.get("edges") or []
                # centralidade aproximada = grau total
                deg = {}
                for e in edges:
                    u, v = e.get("from"), e.get("to")
                    if isinstance(u, str):
                        deg[u] = deg.get(u, 0) + 1
                    if isinstance(v, str):
                        deg[v] = deg.get(v, 0) + 1
                top = sorted(deg.items(), key=lambda kv: kv[1], reverse=True)[:5]
                return {"nodes": len(nodes), "edges": len(edges), "top": [{"path": p, "degree": d} for p, d in top]}

            # --------------------- F15: Strategos v2 (plano priorizado) ----------------
            @app.post("/strategos/plan", dependencies=[Depends(rate_limit(60, 60))])
            def strategos_plan(payload: PlanIn, request: Request = None, response: Response = None):
                """
                Corpo: { logs?: {...}, files?: {path:content}, top_k?: int, weights?: {impact,risk,cost} }
                Retorna: { mode, weights, boosts, nodes_considered, steps[] }
                """
                try:
                    t0 = time.perf_counter()
                    trace_id = (payload.dict() or {}).get("trace_id") or _new_trace_id()
                    payload_dict = payload.dict()
                    payload_dict["trace_id"] = trace_id
                    _validate_json(payload_dict, _SCHEMA_IN, where="input")
                    
                    logs = payload.logs
                    files = payload.files
                    top_k = int(payload_dict.get("top_k") or 8)
                    weights = payload_dict.get("weights") or {}

                    # grafo via CodeMap (fase 8)
                    codemap = {"nodes": [], "edges": []}
                    if CodeMap:
                        try:
                            codemap = CodeMap().build(".")
                        except Exception:
                            pass

                    # episódios (fase 14) para churn
                    episodes = []
                    if EpisodicMemory:
                        try:
                            episodes = EpisodicMemory()._load_episodes()
                        except Exception:
                            episodes = []

                    if not StrategosV2Graph:
                        resp = {"mode": "ADVICE", "steps": [], "reason": "StrategosV2Graph indisponível", "trace_id": trace_id}
                    else:
                        scorer = StrategosV2Graph(weights=weights)
                        plan = scorer.plan(codemap, logs, files, episodes, top_k=top_k)
                        resp = {"ok": True, "trace_id": trace_id, "plan": plan}
                    
                    # trace & cost
                    _validate_json({"trace_id": trace_id}, _SCHEMA_OUT, where="output-min")
                    dt = int((time.perf_counter() - t0) * 1000)
                    rec = {
                        "ts": _utc_iso(),
                        "trace_id": trace_id,
                        "endpoint": "/strategos/plan",
                        "latency_ms": dt,
                        "req_bytes": _summarize_sizes(payload_dict),
                        "res_bytes": _summarize_sizes(resp),
                    }
                    _trace_log(rec)
                    if response is not None:
                        response.headers["X-Trace-Id"] = trace_id
                    return resp
                except Exception as e:
                    return {"ok": False, "error": str(e)}

            @app.post("/run")
            async def run(request):
                try:
                    body = await request.json()
                except Exception:
                    raise HTTPException(400, "Invalid JSON")
                out = _run_core(body)
                return {"diff": out["diff"], "metrics": out["metrics"], "patch_info": out.get("patch_info")}

            @app.post(
                "/research/vanguard/brief",
                dependencies=[Depends(rate_limit(30, 60)), Depends(require_api_key)]
            )
            async def create_vanguard_brief(payload: Dict[str, Any]):
                """
                Gera e valida um Vanguard Brief (pesquisa engenharia-only) e, opcionalmente,
                passa pelo admin gate para promoção ao CANON.

                Body:
                  {
                    "query": "string",                     # obrigatório
                    "sources": [ {title,url,date,...} ],   # opcional (se ausente, tenta radar se existir)
                    "approve": false,                      # opcional: tenta aprovar
                    "approver": "email@org"                # opcional: nome/email do aprovador
                  }
                """
                if generate_brief is None or validate_brief is None or propose_to_canon is None:
                    raise HTTPException(status_code=503, detail="Vanguard modules unavailable")

                query = (payload.get("query") or "").strip()
                if not query:
                    raise HTTPException(status_code=400, detail="Field 'query' is required")

                # fontes opcionais (a UI pode enviar; se não, tenta radar se disponível)
                sources: List[Dict[str, Any]] = payload.get("sources") or []
                if not sources:
                    try:
                        from .research.vanguard_radar import VanguardRadar  # opcional
                        vr = VanguardRadar()
                        sources = vr.search(query) or []
                    except Exception:
                        # Sem radar disponível → segue apenas com o que foi enviado (vazio).
                        sources = []

                brief = generate_brief(query, sources)
                validation = validate_brief(brief)

                approve = bool(payload.get("approve"))
                approver = (payload.get("approver") or "api").strip()
                gate = propose_to_canon(brief, approver=approver, approve=approve)

                return {"brief": brief, "validation": validation, "gate": gate}

            # ---- Trace Badge (último evento) ----
            @app.get("/traces/badge", dependencies=[Depends(rate_limit(60, 60))])
            def traces_badge():
                files = sorted(_TRACE_DIR.glob("trace-*.jsonl"), reverse=True)
                for fn in files:
                    try:
                        with fn.open("r", encoding="utf-8") as f:
                            lines = f.readlines()
                            if not lines:
                                continue
                            # último evento do arquivo mais recente
                            rec = json.loads(lines[-1])
                            req_b = int(rec.get("req_bytes") or 0)
                            res_b = int(rec.get("res_bytes") or 0)
                            tokens_in_est = max(0, req_b // 4)
                            tokens_out_est = max(0, res_b // 4)
                            return {
                                "ok": True,
                                "trace_id": rec.get("trace_id", ""),
                                "ts": rec.get("ts", ""),
                                "endpoint": rec.get("endpoint", ""),
                                "latency_ms": rec.get("latency_ms"),
                                "tokens_in_est": tokens_in_est,
                                "tokens_out_est": tokens_out_est,
                            }
                    except Exception:
                        continue
                return {"ok": True, "trace_id": "", "ts": "", "endpoint": "", "latency_ms": None, "tokens_in_est": 0, "tokens_out_est": 0}

                    # ------------------------------------------------------------
        # F19: Editor Patch API (Cursor/VSCode bridge)
        # ------------------------------------------------------------
        class EditorDiagnostic(BaseModel):
            file: str = Field(..., description="path relativo no workspace")
            code: Optional[str] = Field(None, description="código do diagnóstico (ex. TS2304)")
            message: str = Field(..., description="mensagem do diagnóstico")

        class EditorContext(BaseModel):
            ide: str = Field("vscode", description="vscode|cursor")
            diagnostics: List[EditorDiagnostic] = Field(default_factory=list)

        class EditorPatchIn(BaseModel):
            logs: Dict[str, str] = Field(default_factory=dict)
            files: Dict[str, str] = Field(default_factory=dict, description="arquivo_relativo -> conteúdo")
            context: Optional[EditorContext] = None
            workspace: str = Field("default")
            return_files: bool = Field(True, description="se True, retornar files_out quando seguro")

        class EditorPatchOut(BaseModel):
            mode: str = Field("ADVISORY", description="PATCH|ADVISORY")
            diff: Optional[str] = None
            files_out: Optional[Dict[str, str]] = None
            trace_id: str
            metrics: Dict[str, Any] = Field(default_factory=dict)
            report: Dict[str, Any] = Field(default_factory=dict)

        # util local p/ diff seguro (não-fatal se indisponível)
        def _apply_unified_diff_safe(logs: Dict[str, str],
                                     files: Dict[str, str]) -> Dict[str, Any]:
            """
            Placeholder: você já tem a pipeline que produz o patch.
            Aqui só centralizamos chamada/integração de F13–F17.
            Retorne dict com 'mode','diff','files_out','metrics','report'.
            """
            result: Dict[str, Any] = {
                "mode": "ADVISORY",
                "diff": None,
                "files_out": None,
                "metrics": {},
                "report": {}
            }
            # F13: se ExecutionReranker existir, preferir n-best
            try:
                from llm.rerank.execution_reranker import ExecutionReranker
                rr = ExecutionReranker()
                # exemplo mínimo: 1 candidato gerado pelo seu pipeline
                candidates = logs.get("__candidates__", [])
                if isinstance(candidates, list) and candidates:
                    rr_out = rr.run("editor", candidates, k=min(3, len(candidates)))
                    result["metrics"]["rerank"] = rr_out
                    # se vencedor for 'files_out' inline (sua CLI pode já produzir)
                    if rr_out.get("winner", {}).get("files_out"):
                        result["mode"] = "PATCH"
                        result["files_out"] = rr_out["winner"]["files_out"]
                        return result
                    if rr_out.get("winner", {}).get("diff"):
                        result["mode"] = "PATCH"
                        result["diff"] = rr_out["winner"]["diff"]
                        return result
            except Exception:
                pass

            # F14: priors de memória episódica (se disponível)
            try:
                from llm.memory.episodic import EpisodicMemory
                em = EpisodicMemory()
                em.apply_priors({"files": files}, logs, {})
                result["metrics"]["memory_priors"] = em.metrics()
            except Exception:
                pass

            # F15: Strategos v2 (se disponível)
            try:
                from llm.strategos.scorer_v2 import StrategosV2Graph
                sg = StrategosV2Graph()
                plan = sg.plan({"nodes": [], "edges": []}, logs, files)
                result["report"]["plan"] = plan
                result["metrics"]["strategos"] = {
                    "attempts_to_green_est": plan.get("attempts_to_green_est"),
                    "mode": plan.get("mode")
                }
            except Exception:
                pass

            # Se chegou até aqui sem patch seguro, devolve ADVISORY
            return result

        @router.post(
            "/editor/patch",
            response_model=EditorPatchOut,
            dependencies=[Depends(rate_limit(30, 60)), Depends(require_api_key)]
        )
        def editor_patch(req: EditorPatchIn, request: Request, response: Response):
            """
            Interface única para VSCode/Cursor:
            - recebe arquivos abertos + diagnósticos
            - tenta produzir PATCH (diff/files_out) ou ADVISORY
            - devolve trace_id e métricas (hook F16/F19)
            """
            trace_id = _ensure_trace_id(response)
            try:
                out = _apply_unified_diff_safe(req.logs or {}, req.files or {})
                mode = out.get("mode", "ADVISORY")
                diff = out.get("diff")
                files_out = out.get("files_out")

                # badge Strategos (se registrado no app.state)
                try:
                    app = request.app
                    badge = {
                        "mode": out.get("metrics", {}).get("strategos", {}).get("mode", mode),
                        "attempts_to_green_est": out.get("metrics", {}).get("strategos", {}).get("attempts_to_green_est", None),
                        "ts": None
                    }
                    if hasattr(app.state, "STRATEGOS_BADGE"):
                        app.state.STRATEGOS_BADGE = badge
                except Exception:
                    pass

                return EditorPatchOut(
                    mode=mode,
                    diff=diff,
                    files_out=files_out if req.return_files else None,
                    metrics=out.get("metrics", {}),
                    report=out.get("report", {}),
                    trace_id=trace_id
                )
            except HTTPException:
                raise
            except Exception as e:
                # Mantém observabilidade (F16)
                raise HTTPException(status_code=503, detail=f"editor/patch unavailable: {e}")

        # -------- KPIs: export + badge --------
        def _collect_kpis_now():
            try:
                from evals.kpis.export_kpis import _collect as _collect_raw  # type: ignore
                snap = _collect_raw()
                return {
                    "ts": snap.get("ts"),
                    "golden_sr": snap.get("golden_success_rate"),
                    "redteam_rate": snap.get("redteam_denials_rate"),
                    "repeat_error_rate": snap.get("repeat_error_rate"),
                    "requests_today": snap.get("requests_today"),
                    "latency_ms_p95": snap.get("latency_ms_p95"),
                }
            except Exception:
                return app.state.KPI_BADGE

            @app.get("/kpis/export", dependencies=[Depends(rate_limit(30, 60))])
            def kpis_export(format: str = "json"):
                """On-demand aggregação dos KPIs do dia (JSON ou CSV)."""
                from evals.kpis.export_kpis import main as run_export  # type: ignore
                # roda export e retorna snapshot/paths
                try:
                    run_export()
                except SystemExit:
                    pass
                # retorna badge/preview
                badge = _collect_kpis_now()
                if format.lower() == "csv":
                    return {"ok": True, "format": "csv", "badge": badge, "path": ".fortaleza/kpis/daily.csv"}
                return {"ok": True, "format": "json", "badge": badge, "path": f".fortaleza/kpis/kpis-{datetime.now().strftime('%Y%m%d')}.json"}

            @app.get("/kpis/badge", dependencies=[Depends(rate_limit(60, 60))])
            def get_kpi_badge():
                # se não houver em memória, coleta on-demand
                b = app.state.KPI_BADGE or {}
                if not b.get("ts"):
                    b = _collect_kpis_now()
                return b

            class KPIBadgeIn(BaseModel):
                ts: Optional[str] = None
                golden_sr: Optional[float] = None
                redteam_rate: Optional[float] = None
                repeat_error_rate: Optional[float] = None
                requests_today: Optional[int] = None
                latency_ms_p95: Optional[float] = None

            @app.post("/kpis/badge", dependencies=[Depends(rate_limit(20, 60)), Depends(require_api_key)])
            def post_kpi_badge(body: KPIBadgeIn):
                """Permite um job diário publicar o snapshot (ex.: via cron/CI)."""
                snap = body.model_dump()
                snap["ts"] = snap.get("ts") or datetime.utcnow().isoformat(timespec="seconds")+"Z"
                app.state.KPI_BADGE = snap
                return {"ok": True, "badge": snap}

            return app

        return _build_app()

    except ImportError:
        # Fallback para WSGI micro
        def app(environ, start_response):
            if environ["REQUEST_METHOD"] == "POST" and environ["PATH_INFO"] == "/run":
                try:
                    content_length = int(environ.get("CONTENT_LENGTH", 0))
                    body = environ["wsgi.input"].read(content_length).decode()
                    data = json.loads(body)
                    out = _run_core(data)
                    status, headers, body = _json_response(out)
                except Exception as e:
                    status, headers, body = _json_response({"error": str(e)}, 400)
            else:
                status, headers, body = _json_response({"error": "Not found"}, 404)
            
            start_response(f"{status} OK", headers)
            return [body.encode()]

        return app

app = create_app()

if __name__ == "__main__":
    # Execução direta: uvicorn se existir; senão HTTPServer básico
    try:
        import uvicorn
        uvicorn.run("fortaleza-llm.llm.server:app", host="0.0.0.0", port=int(os.getenv("PORT","8001")), reload=False)
    except Exception:
        from wsgiref.simple_server import make_server
        srv = make_server("0.0.0.0", int(os.getenv("PORT","8001")), app)
        print("LLM server listening on", srv.server_address)
        srv.serve_forever()
