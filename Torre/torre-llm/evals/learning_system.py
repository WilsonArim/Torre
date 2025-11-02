from __future__ import annotations
import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from .codemods.ts_imports import ensure_import  # TS2304 (imports seguros)
from .codemods.ts_module_decl import ensure_module_decl  # TS2307 (ambient module)
from .codemods.ts_ambient_kits import ensure_ambient_kit  # kits (assets/jsx/node/tests)
try:
    from llm.memory.episodic import EpisodicMemory, Episode
except Exception:
    EpisodicMemory = None
    Episode = None
from fnmatch import fnmatch

_TS_CODE_RE = re.compile(r"\bTS(?P<code>\d{3,5})\b", re.I)
_PY_ERR_RE  = re.compile(r"\b(?P<exc>[A-Z][A-Za-z]+Error)\b")

# Mapeia códigos/assinaturas comuns → sinónimos úteis para aumentar recall
_ERROR_SYNONYMS = {
    "TS2304": ["cannot find name", "is not defined"],
    "TS2580": ["cannot find name require", "types for node", "typings for node"],
    "ModuleNotFoundError": ["cannot find module", "no module named", "import error"],
}

@dataclass
class Lesson:
    id: str
    signature: Dict[str, Any]            # {"error_code": "TS2304", "path_glob": "src/**", "toolchain": "vite"}
    action: Dict[str, Any]               # {"kind": "codemod"|"prompt_nudge"|..., "params": {...}}
    stats: Dict[str, Any] = field(default_factory=lambda: {"applied":0,"wins":0,"fails":0,"last_ts":0})
import json, time, pathlib
from typing import Dict, Any, List, Set, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict

@dataclass
class Episode:
    """Episódio de aprendizagem"""
    timestamp: float
    error_type: str
    error_content: str
    solution_applied: str
    success: bool
    ttg_ms: int
    diff_size: int
    violations: List[str]
    module_affected: str

@dataclass
class Lesson:
    """Lição aprendida de episódios"""
    id: str
    signature: Dict[str, Any]            # {"error_code": "TS2304", "path_glob": "src/**", "toolchain": "vite"}
    action: Dict[str, Any]               # {"kind": "codemod"|"prompt_nudge"|..., "params": {...}}
    stats: Dict[str, Any] = field(default_factory=lambda: {"applied":0,"wins":0,"fails":0,"last_ts":0})
    # Campos legados para compatibilidade
    pattern: str = ""
    error_type: str = ""
    solution_template: str = ""
    success_rate: float = 0.0
    avg_ttg: float = 0.0
    avg_diff_size: float = 0.0
    frequency: int = 0
    last_seen: float = 0.0
    confidence: float = 0.0

class LearningSystem:
    """
    Workspace-local learning:
      - match com score ponderado (erro 0.6, caminho 0.25, toolchain 0.15)
      - cooldown anti-loop (não reaplicar lição com falhas consecutivas)
      - aplica se confiança >= 0.50 (com bónus anti-repetição e prior de sucesso)
    """
    MIN_CONF = 0.50
    # se corresponder exatamente (erro + path_glob) e não estiver em cooldown,
    # permite aplicar com confiança um pouco abaixo do limiar "geral"
    FORCE_APPLY_CONF = 0.40
    FAIL_COOLDOWN = 2       # não reaplicar se houve >=2 falhas consecutivas recentes
    FAIL_WINDOW_S  = 60.0   # janela para considerar falhas (segundos)
    STREAK_THRESHOLD = 2    # nº de repetições para acionar bónus anti-repetição

    def __init__(self, storage_path: str = ".fortaleza/learning"):
        self.storage_path = pathlib.Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.lessons: Dict[str, Lesson] = {}  # Mantém compatibilidade com estrutura antiga
        self.episodes: List[Dict[str, Any]] = []
        # memória volátil
        self._recent_fails: Dict[str, List[float]] = {}
        self._streak: Dict[str, int] = {}  # chave: (err|path_glob)
        
        # Carrega dados existentes
        self._load_data()
    
    def record_episode(self, 
                      error_type: str,
                      error_content: str,
                      solution_applied: str,
                      success: bool,
                      ttg_ms: int,
                      diff_size: int,
                      violations: List[str],
                      module_affected: str) -> None:
        """Regista um episódio de aprendizagem"""
        episode = Episode(
            timestamp=time.time(),
            error_type=error_type,
            error_content=error_content,
            solution_applied=solution_applied,
            success=success,
            ttg_ms=ttg_ms,
            diff_size=diff_size,
            violations=violations,
            module_affected=module_affected
        )
        
        self.episodes.append(episode)
        self._update_lessons(episode)
        self._save_episode(episode)
    
    def get_suggested_solution(self, error_content: str, error_type: str) -> Optional[str]:
        """Sugere solução baseada em lições aprendidas"""
        # Procura por padrões similares
        best_match = None
        best_confidence = 0.0
        
        for lesson_id, lesson in self.lessons.items():
            if lesson.error_type == error_type:
                # Calcula similaridade simples
                similarity = self._calculate_similarity(error_content, lesson.pattern)
                if similarity > 0.7 and lesson.confidence > best_confidence:
                    best_match = lesson
                    best_confidence = lesson.confidence
        
        if best_match and best_confidence > 0.8:
            return best_match.solution_template
        
        return None
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de aprendizagem"""
        if not self.episodes:
            return {"total_episodes": 0, "total_lessons": 0, "repetition_rate": 0.0}
        
        # Calcula taxa de repetição de erros
        error_counts = defaultdict(int)
        for episode in self.episodes:
            error_key = f"{episode.error_type}:{episode.error_content[:50]}"
            error_counts[error_key] += 1
        
        repeated_errors = sum(1 for count in error_counts.values() if count > 1)
        total_unique_errors = len(error_counts)
        repetition_rate = (repeated_errors / total_unique_errors * 100) if total_unique_errors > 0 else 0
        
        # Calcula métricas de sucesso
        successful_episodes = [e for e in self.episodes if e.success]
        success_rate = (len(successful_episodes) / len(self.episodes)) * 100
        
        return {
            "total_episodes": len(self.episodes),
            "total_lessons": len(self.lessons),
            "repetition_rate": round(repetition_rate, 2),
            "success_rate": round(success_rate, 2),
            "avg_ttg": sum(e.ttg_ms for e in self.episodes) / len(self.episodes),
            "avg_diff_size": sum(e.diff_size for e in self.episodes) / len(self.episodes),
            "lessons_by_type": self._get_lessons_by_type()
        }
    
    def _update_lessons(self, episode: Episode) -> None:
        """Atualiza lições baseado no episódio"""
        # Extrai padrão do erro
        pattern = self._extract_pattern(episode.error_content)
        lesson_id = f"{episode.error_type}:{pattern}"
        
        if lesson_id in self.lessons:
            # Atualiza lição existente
            lesson = self.lessons[lesson_id]
            lesson.frequency += 1
            lesson.last_seen = episode.timestamp
            
            # Atualiza métricas
            if episode.success:
                lesson.success_rate = ((lesson.success_rate * (lesson.frequency - 1)) + 1.0) / lesson.frequency
            else:
                lesson.success_rate = (lesson.success_rate * (lesson.frequency - 1)) / lesson.frequency
            
            lesson.avg_ttg = ((lesson.avg_ttg * (lesson.frequency - 1)) + episode.ttg_ms) / lesson.frequency
            lesson.avg_diff_size = ((lesson.avg_diff_size * (lesson.frequency - 1)) + episode.diff_size) / lesson.frequency
            
            # Atualiza confiança
            lesson.confidence = min(1.0, lesson.frequency * 0.1 + lesson.success_rate * 0.5)
        else:
            # Cria nova lição
            lesson = Lesson(
                id=lesson_id,
                signature={"error_code": episode.error_type, "pattern": pattern},
                action={"kind": "prompt_nudge"},
                pattern=pattern,
                error_type=episode.error_type,
                solution_template=episode.solution_applied,
                success_rate=1.0 if episode.success else 0.0,
                avg_ttg=episode.ttg_ms,
                avg_diff_size=episode.diff_size,
                frequency=1,
                last_seen=episode.timestamp,
                confidence=0.5 if episode.success else 0.2
            )
            self.lessons[lesson_id] = lesson
        
        # Salva lição atualizada
        self._save_lesson(lesson_id, lesson)
    
    # ---------- Helpers ----------
    def _extract_error_code(self, text: str) -> Optional[str]:
        m = _TS_CODE_RE.search(text)
        if m:
            return f"TS{m.group('code')}"
        m = _PY_ERR_RE.search(text)
        if m:
            return m.group("exc")
        # fallback: tenta casar por sinónimos
        for code, syns in _ERROR_SYNONYMS.items():
            if any(s in text for s in syns):
                return code
        return None

    def _infer_toolchain(self, text: str) -> Optional[str]:
        if "vite" in text: return "vite"
        if "webpack" in text: return "webpack"
        if "pytest" in text or "traceback" in text: return "pytest"
        if "jest" in text: return "jest"
        if "tsc" in text: return "tsc"
        return None

    def _guess_path_glob(self, ep: Dict[str, Any]) -> Optional[str]:
        p = (ep.get("file") or ep.get("path") or ep.get("module") or "").strip()
        if not p:
            return None
        # heurística leve: se está em src/, usar prefixo
        if "/src/" in p:
            base = p.split("/src/", 1)[0]
            return f"{base}/src/**"
        if p.endswith(".ts") or p.endswith(".tsx") or p.endswith(".py") or p.endswith(".js") or p.endswith(".jsx"):
            # mesma pasta
            folder = p.rsplit("/", 1)[0] if "/" in p else "."
            return f"{folder}/**"
        return None

    def _confidence(self, lesson: Lesson, msg: str, err_code: Optional[str], tool: Optional[str], file_hint: str) -> float:
        sig = lesson.signature or {}
        score = 0.0
        # 0.6 — erro
        l_err = (sig.get("error_code") or "").lower()
        if l_err:
            if err_code and l_err == err_code.lower():
                score += 0.6
            else:
                # sinónimos ajudam recall
                syns = _ERROR_SYNONYMS.get(l_err.upper(), [])
                if any(s in msg for s in syns):
                    score += 0.45
        # 0.25 — caminho
        l_glob = sig.get("path_glob")
        if l_glob and file_hint:
            try:
                if fnmatch(file_hint, l_glob):
                    score += 0.25
            except Exception:
                pass
        # 0.15 — toolchain
        l_tool = (sig.get("toolchain") or "").lower()
        if l_tool and tool and l_tool == tool.lower():
            score += 0.15
        # prior de sucesso (até +0.10)
        score += self._success_prior(lesson)
        return min(1.0, score)

    def _success_prior(self, lesson: Lesson) -> float:
        st = lesson.stats or {}
        applied = max(1, int(st.get("applied", 0)))
        wins = int(st.get("wins", 0))
        wr = wins / applied
        return min(0.10, 0.10 * wr)

    def _is_in_cooldown(self, lesson_id: str, now: float) -> bool:
        fails = [t for t in self._recent_fails.get(lesson_id, []) if now - t <= self.FAIL_WINDOW_S]
        self._recent_fails[lesson_id] = fails
        return len(fails) >= self.FAIL_COOLDOWN

    # APIs para registrar outcome e expor métricas aos testes
    def register_outcome(self, lesson_id: str, success: bool):
        now = time.time()
        for l in self.lessons:
            if l.id == lesson_id:
                if success:
                    l.stats["wins"] += 1
                else:
                    l.stats["fails"] += 1
                    self._recent_fails.setdefault(lesson_id, []).append(now)
                l.stats["last_ts"] = now
                break

    def choose_and_apply(self, logs: dict, request: dict, context: dict | None = None) -> dict:
        """
        Fluxo de alto nível usado pelos testes:
          - ordena por confiança
          - aplica a primeira >= MIN_CONF e fora de cooldown
          - injeta métricas no request["meta"]
        """
        ranked = self.match(logs, context)
        meta = request.setdefault("meta", {})
        meta["lesson_applied"] = None
        meta["lesson_confidence"] = 0.0
        meta["reduction_estimate"] = 0.0
        meta["codemod"] = None
        meta["codemods"] = []
        # chave de streak do erro/caminho atual
        msg = (" ".join(str(v) for v in (logs or {}).values())).lower()
        err_code = self._extract_error_code(msg) or ""
        file_hint = (context or {}).get("file") or (context or {}).get("path") or ""
        glob_hint = self._guess_path_glob({"file": file_hint}) or ""
        streak_key = f"{err_code}|{glob_hint}"
        streak = self._streak.get(streak_key, 0)
        # capturar símbolo antes da conversão para minúsculas
        original_msg = " ".join(str(v) for v in (logs or {}).values())
        for cand in ranked:
            lesson: "Lesson" = cand["lesson"]
            conf = float(cand["confidence"])
            exact = self._exact_signature_match(lesson, err_code, file_hint)
            # bónus anti-repetição leve (até +0.10) se mesmo erro reaparece neste caminho
            if streak >= self.STREAK_THRESHOLD and conf >= self.FORCE_APPLY_CONF:
                conf = min(1.0, conf + 0.10)
            # gating: aplica se (conf >= MIN) ou (match exato e conf >= FORCE_APPLY_CONF)
            if (conf < self.MIN_CONF and not (exact and conf >= self.FORCE_APPLY_CONF)) \
               or self._is_in_cooldown(lesson.id, time.time()):
                continue
            req2 = self.apply(lesson, request)
            applied_any = False

            # —— TS2304: Cannot find name <Symbol> ——
            if err_code == "TS2304":
                # extrair símbolo preservando capitalização a partir de raw_msg
                m = re.search(r"Cannot\s+find\s+name\s+['\"]?([A-Za-z_][A-Za-z0-9_]*)['\"]?", original_msg, re.I)
                sym = m.group(1) if m else None
                target = (context or {}).get("file")
                if sym and target and (target.endswith(".ts") or target.endswith(".tsx")):
                    content = (req2.get("files") or {}).get(target)
                    if isinstance(content, str) and content:
                        # heurística: preferir vitest se logs mencionam 'vite'/'vitest'; jest se 'jest'
                        prefer_pkg = "vitest" if ("vite" in msg or "vitest" in msg) else ("jest" if "jest" in msg else None)
                        new_src, changed = ensure_import(content, sym, prefer_pkg=prefer_pkg)
                        if changed:
                            req2["files"][target] = new_src
                            meta["codemods"].append(f"ts_missing_symbol:{sym}")
                            meta["codemod_path"] = target
                            applied_any = True

            # —— TS2307: Cannot find module '<id>' ——
            if err_code == "TS2307":
                m = re.search(r"Cannot\s+find\s+module\s+['\"]([^'\"]+)['\"]", original_msg, re.I)
                module_id = m.group(1) if m else None
                if module_id:
                    # ativos conhecidos → kit 'assets'
                    if any(module_id.endswith(ext) for ext in (".css", ".scss", ".svg", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".json")):
                        fpath, files_map, changed = ensure_ambient_kit(req2.get("files") or {}, "assets")
                        if changed:
                            req2["files"] = files_map
                            meta["codemods"].append(f"ts_assets_ambient:{module_id}")
                            meta["codemod_path"] = fpath
                            applied_any = True
                    # fallback genérico: declare module '<id>'
                    fpath, files_map, changed = ensure_module_decl(req2.get("files") or {}, module_id)
                    if changed:
                        req2["files"] = files_map
                        meta["codemods"].append(f"ts_missing_module:{module_id}")
                        meta["codemod_path"] = fpath
                        applied_any = True

            # —— Kits contextuais por mensagem ——
            # JSX implicit any / ambiente JSX ausente
            if ("jsx element implicitly has type 'any'" in msg) or ("intrinsic elements" in msg):
                fpath, files_map, changed = ensure_ambient_kit(req2.get("files") or {}, "jsx")
                if changed:
                    req2["files"] = files_map
                    meta["codemods"].append("ts_jsx_intrinsics:any")
                    meta["codemod_path"] = fpath
                    applied_any = True

            # Globals Node em projeto TS/SPA (process/Buffer frequentemente usados em build)
            if ("cannot find name process" in msg) or ("cannot find name buffer" in msg):
                fpath, files_map, changed = ensure_ambient_kit(req2.get("files") or {}, "node")
                if changed:
                    req2["files"] = files_map
                    meta["codemods"].append("ts_node_globals:any")
                    meta["codemod_path"] = fpath
                    applied_any = True

            # Tipos de testes ausentes
            if ("jest" in msg) or ("@types/jest" in msg):
                fpath, files_map, changed = ensure_ambient_kit(req2.get("files") or {}, "tests-jest")
                if changed:
                    req2["files"] = files_map
                    meta["codemods"].append("ts_tests_globals:jest")
                    meta["codemod_path"] = fpath
                    applied_any = True
            elif ("vitest" in msg) or ("@types/vitest" in msg):
                fpath, files_map, changed = ensure_ambient_kit(req2.get("files") or {}, "tests-vitest")
                if changed:
                    req2["files"] = files_map
                    meta["codemods"].append("ts_tests_globals:vitest")
                    meta["codemod_path"] = fpath
                    applied_any = True

            # meta/redução estimada agressiva se mais de um codemod aplicado
            if applied_any:
                meta["reduction_estimate"] = 0.9 if len(meta["codemods"]) >= 2 else 0.85
                meta["lesson_applied"] = meta.get("lesson_applied") or "auto-codemod"
            # grava episódio leve (sem PII)
            if EpisodicMemory and Episode:
                em = EpisodicMemory()
                em.append(Episode.build({
                    "file": (context or {}).get("file"),
                    "err_code": err_code,
                    "err_msg": original_msg,
                    "toolchain": (context or {}).get("toolchain"),
                    "action": "codemod" if applied_any else "patch",
                    "outcome": "unknown",
                    "meta": {"codemods": meta.get("codemods", [])},
                }))
                em.promote_rules()
            meta["lesson_applied"] = lesson.id
            meta["lesson_confidence"] = round(conf, 3)
            meta["reduction_estimate"] = round(min(0.9, 0.5 + 0.5*conf), 3)
            # telemetria e prior de sucesso precisam de stats vivos
            st = lesson.stats or {}
            st["applied"] = int(st.get("applied", 0)) + 1
            lesson.stats = st
            # após aplicar, zera o streak local para refletir "redução" e evitar loops
            if streak_key in self._streak:
                self._streak[streak_key] = 0
            return req2
        return request

    def _extract_pattern(self, error_content: str) -> str:
        """Extrai padrão do erro"""
        # Implementação simplificada - extrai palavras-chave
        keywords = []
        
        # Padrões comuns
        patterns = [
            r"Cannot find name '([^']+)'",
            r"Module '([^']+)' not found",
            r"Property '([^']+)' does not exist",
            r"Type '([^']+)' has no property",
            r"TS(\d+):",
        ]
        
        import re
        for pattern in patterns:
            match = re.search(pattern, error_content)
            if match:
                keywords.append(match.group(1) if match.groups() else match.group(0))
        
        # Adiciona tipo de erro se não encontrou padrões específicos
        if not keywords:
            keywords = [error_content.split()[0]]  # Primeira palavra
        
        return " ".join(keywords[:3])  # Máximo 3 keywords
    
    def _calculate_similarity(self, content1: str, content2: str) -> float:
        """Calcula similaridade entre dois conteúdos (0-1)"""
        # Implementação simples baseada em palavras comuns
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _get_lessons_by_type(self) -> Dict[str, int]:
        """Retorna número de lições por tipo de erro"""
        lesson_counts = defaultdict(int)
        for lesson in self.lessons.values():
            lesson_counts[lesson.error_type] += 1
        return dict(lesson_counts)
    
    def _save_episode(self, episode: Episode) -> None:
        """Salva episódio em ficheiro"""
        episode_file = self.storage_path / f"episode_{int(episode.timestamp)}.json"
        with open(episode_file, 'w') as f:
            json.dump(asdict(episode), f, indent=2)
    
    def _save_lesson(self, lesson_id: str, lesson: Lesson) -> None:
        """Salva lição em ficheiro"""
        lessons_file = self.storage_path / "lessons.json"
        lessons_data = {lesson_id: asdict(lesson)}
        
        # Carrega lições existentes
        if lessons_file.exists():
            with open(lessons_file, 'r') as f:
                existing_lessons = json.load(f)
            existing_lessons.update(lessons_data)
        else:
            existing_lessons = lessons_data
        
        # Salva todas as lições
        with open(lessons_file, 'w') as f:
            json.dump(existing_lessons, f, indent=2)
    
    def _load_data(self) -> None:
        """Carrega dados salvos"""
        # Carrega episódios
        for episode_file in self.storage_path.glob("episode_*.json"):
            try:
                with open(episode_file, 'r') as f:
                    data = json.load(f)
                    episode = Episode(**data)
                    self.episodes.append(episode)
            except Exception as e:
                print(f"⚠️ Erro ao carregar episódio {episode_file}: {e}")
        
        # Carrega lições
        lessons_file = self.storage_path / "lessons.json"
        if lessons_file.exists():
            try:
                with open(lessons_file, 'r') as f:
                    lessons_data = json.load(f)
                    for lesson_id, lesson_dict in lessons_data.items():
                        lesson = Lesson(**lesson_dict)
                        self.lessons[lesson_id] = lesson
            except Exception as e:
                print(f"⚠️ Erro ao carregar lições: {e}")
    
    def generate_learning_report(self) -> str:
        """Gera relatório de aprendizagem"""
        stats = self.get_learning_stats()
        
        report = f"""
# Relatório de Aprendizagem Persistente v1

## Resumo
- **Total de Episódios**: {stats['total_episodes']}
- **Total de Lições**: {stats['total_lessons']}
- **Taxa de Repetição**: {stats['repetition_rate']}%
- **Taxa de Sucesso**: {stats['success_rate']}%
- **TTG Médio**: {stats['avg_ttg']:.1f}ms
- **Diff Size Médio**: {stats['avg_diff_size']:.1f} linhas

## Lições por Tipo
"""
        
        for error_type, count in stats['lessons_by_type'].items():
            report += f"- **{error_type}**: {count} lições\n"
        
        report += f"""
## Status dos Gates
- ✅ **Repetição de erro ↓ ≥60%**: {'✅' if stats['repetition_rate'] <= 40 else '❌'} ({stats['repetition_rate']}%)
- ✅ **Success rate ≥95%**: {'✅' if stats['success_rate'] >= 95 else '❌'} ({stats['success_rate']}%)

## Lições Mais Confiáveis
"""
        
        # Top 5 lições por confiança
        top_lessons = sorted(self.lessons.values(), key=lambda l: l.confidence, reverse=True)[:5]
        for i, lesson in enumerate(top_lessons, 1):
            report += f"""
### {i}. {lesson.error_type.upper()} (Confiança: {lesson.confidence:.2f})
- **Padrão**: {lesson.pattern}
- **Sucesso**: {lesson.success_rate:.1%}
- **Frequência**: {lesson.frequency} vezes
- **Última vez**: {time.strftime('%Y-%m-%d %H:%M', time.localtime(lesson.last_seen))}
"""
        
        return report

    def add_episode(self, episode: dict):
        self.episodes.append(episode)
        # atualizar streak (erro + caminho inferido)
        try:
            err = (episode.get("error") or episode.get("logs") or "").lower()
            code = self._extract_error_code(err) or ""
            glob = episode.get("path_glob") or self._guess_path_glob(episode) or ""
            key = f"{code}|{glob}"
            if key.strip("|"):
                self._streak[key] = self._streak.get(key, 0) + 1
        except Exception:
            pass

    def _exact_signature_match(self, lesson: "Lesson", err_code: str, file_hint: str) -> bool:
        sig = getattr(lesson, "signature", {}) or {}
        l_err = (sig.get("error_code") or "").lower()
        l_glob = (sig.get("path_glob") or "").lower()
        fh = (file_hint or "").lower()
        return bool(l_err and l_err == (err_code or "").lower() and l_glob and l_glob in fh)

    def extract_lessons(self):
        """
        Extrai lições simples a partir de episódios:
        - Detecta código de erro (TS/Python)
        - Infere path_glob por localização (se houver)
        - Armazena como Lesson dataclass
        """
        buckets: Dict[Tuple[str,str,str], int] = {}
        for ep in self.episodes:
            # Handle both dict and Episode objects
            if hasattr(ep, 'error_content'):
                msg = ep.error_content.strip().lower()
                path_glob = ep.module_affected or ""
            else:
                msg = (ep.get("error") or ep.get("logs") or "").strip().lower()
                path_glob = ep.get("path_glob") or self._guess_path_glob(ep) or ""
            
            if not msg:
                continue
            err_code = self._extract_error_code(msg)
            tool     = self._infer_toolchain(msg)
            key = (err_code or "", path_glob or "", tool or "")
            buckets.setdefault(key, 0)
            buckets[key] += 1

        self.lessons = {}
        for i, ((err, glob, tool), _) in enumerate(sorted(buckets.items(), key=lambda x: x[1], reverse=True)):
            sig = {"error_code": err or None, "path_glob": glob or None, "toolchain": tool or None}
            lesson_id = f"auto-{i}"
            self.lessons[lesson_id] = Lesson(id=lesson_id, signature=sig, action={"kind":"prompt_nudge"})

    def match(self, logs: dict, context: dict | None = None) -> List[Dict[str, Any]]:
        """
        Devolve lições compatíveis, com score/confidence calculados.
        """
        msg = (" ".join(str(v) for v in (logs or {}).values())).lower()
        err_code = self._extract_error_code(msg)
        tool     = self._infer_toolchain(msg)
        file_hint = (context or {}).get("file") or (context or {}).get("path") or ""

        matches: List[Dict[str, Any]] = []
        for lesson in self.lessons.values():
            conf = self._confidence(lesson, msg, err_code, tool, file_hint)
            matches.append({
                "lesson": lesson,
                "confidence": conf,
            })
        matches.sort(key=lambda x: x["confidence"], reverse=True)
        return matches

    def apply(self, lesson: Lesson, request: dict) -> dict:
        """
        Aplica lição se confiança suficiente e não em cooldown.
        """
        now = time.time()
        if self._is_in_cooldown(lesson.id, now):
            return request  # não aplica

        request = dict(request or {})
        meta = request.setdefault("meta", {})
        meta["lesson_applied"] = lesson.id
        meta["lesson_action"]  = lesson.action
        lesson.stats["applied"] += 1
        lesson.stats["last_ts"]  = now
        return request
