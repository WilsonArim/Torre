#!/usr/bin/env python3
"""
Funções auxiliares para validações de linguagem e arquétipo (Mini-PIN)
"""

import json
import re
import subprocess
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, List

REPO_ROOT = Path(__file__).resolve().parents[2]
TORRE_ROOT = REPO_ROOT / "torre"
TORRE_RELATORIOS = TORRE_ROOT / "relatorios"


def detect_language(file_path: Path) -> Tuple[str, float]:
    """
    Detecta linguagem de um arquivo e retorna (linguagem, confiança).
    """
    if not file_path.exists():
        return "unknown", 0.0
    
    ext = file_path.suffix.lower()
    content = file_path.read_text(encoding="utf-8", errors="ignore")[:1000]
    
    # Mapeamento de extensões
    ext_map = {
        ".py": ("python", 0.95),
        ".js": ("javascript", 0.90),
        ".ts": ("typescript", 0.90),
        ".tsx": ("typescript", 0.90),
        ".jsx": ("javascript", 0.90),
        ".java": ("java", 0.95),
        ".c": ("c", 0.90),
        ".cpp": ("cpp", 0.90),
        ".cc": ("cpp", 0.90),
        ".cxx": ("cpp", 0.90),
        ".h": ("c", 0.85),
        ".hpp": ("cpp", 0.85),
        ".go": ("go", 0.95),
        ".rs": ("rust", 0.95),
        ".rb": ("ruby", 0.95),
        ".php": ("php", 0.95),
        ".swift": ("swift", 0.95),
        ".kt": ("kotlin", 0.95),
        ".scala": ("scala", 0.95),
        ".clj": ("clojure", 0.90),
        ".sh": ("bash", 0.85),
        ".yaml": ("yaml", 0.90),
        ".yml": ("yaml", 0.90),
        ".json": ("json", 0.95),
        ".md": ("markdown", 0.95),
    }
    
    lang, conf = ext_map.get(ext, ("unknown", 0.5))
    
    # Validação adicional por conteúdo
    if lang == "python" and ("def " in content or "import " in content):
        conf = min(conf + 0.05, 1.0)
    elif lang == "javascript" and ("function " in content or "const " in content or "require(" in content):
        conf = min(conf + 0.05, 1.0)
    elif lang == "typescript" and ("interface " in content or "type " in content or ": " in content):
        conf = min(conf + 0.05, 1.0)
    
    return lang, conf


def generate_language_profile(files: List[Path]) -> Dict[str, Any]:
    """
    Gera language_profile.json com análise de linguagens dos arquivos.
    """
    profile = {
        "files_analyzed": len(files),
        "languages": {},
        "files_by_language": {},
        "confidence_avg": {},
    }
    
    for file_path in files:
        lang, conf = detect_language(file_path)
        
        if lang not in profile["languages"]:
            profile["languages"][lang] = {"count": 0, "confidence_sum": 0.0, "files": []}
        
        profile["languages"][lang]["count"] += 1
        profile["languages"][lang]["confidence_sum"] += conf
        profile["languages"][lang]["files"].append(str(file_path.relative_to(REPO_ROOT)))
        
        if lang not in profile["files_by_language"]:
            profile["files_by_language"][lang] = []
        profile["files_by_language"][lang].append(str(file_path.relative_to(REPO_ROOT)))
    
    # Calcular média de confiança por linguagem
    for lang, data in profile["languages"].items():
        if data["count"] > 0:
            profile["confidence_avg"][lang] = round(data["confidence_sum"] / data["count"], 3)
    
    return profile


def archetype_check(file_path: Path, language: str) -> Tuple[bool, str]:
    """
    Verifica conformidade com arquétipos da linguagem.
    Retorna (pass, message).
    """
    if not file_path.exists():
        return False, "Arquivo não encontrado"
    
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    
    # Verificações básicas por linguagem
    if language == "python":
        # Verificar imports no topo
        lines = content.split("\n")
        imports_found = False
        code_found = False
        for i, line in enumerate(lines[:20]):  # Primeiras 20 linhas
            stripped = line.strip()
            if stripped.startswith("import ") or stripped.startswith("from "):
                imports_found = True
            elif stripped and not stripped.startswith("#") and not stripped.startswith('"""'):
                if imports_found:
                    code_found = True
                elif not code_found:
                    return False, "Imports devem estar no topo do arquivo"
        
        # Verificar docstrings em funções principais
        if "def " in content and '"""' not in content[:500]:
            return True, "WARN: Docstrings ausentes (não crítico)"
        
        return True, "PASS"
    
    elif language in ["javascript", "typescript"]:
        # Verificar exports/modules
        if "export " not in content and "module.exports" not in content:
            return True, "WARN: Sem exports explícitos (não crítico)"
        
        return True, "PASS"
    
    elif language == "java":
        # Verificar package declaration
        if "package " not in content.split("\n")[0]:
            return False, "Package declaration ausente"
        
        return True, "PASS"
    
    else:
        # Para outras linguagens, aceitar por padrão
        return True, "PASS"


def cross_smells(file_path: Path) -> Tuple[int, List[str]]:
    """
    Detecta code smells e retorna (count, lista de smells).
    """
    if not file_path.exists():
        return 0, []
    
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    smells = []
    
    lines = content.split("\n")
    
    # Long method smell (>50 linhas de código)
    code_lines = [l for l in lines if l.strip() and not l.strip().startswith("#")]
    if len(code_lines) > 200:
        smells.append(f"Long file: {len(code_lines)} linhas de código")
    
    # Magic numbers
    magic_numbers = re.findall(r'\b\d{3,}\b', content)
    if len(magic_numbers) > 5:
        smells.append(f"Magic numbers: {len(magic_numbers)} encontrados")
    
    # Deep nesting (>4 níveis)
    max_indent = 0
    for line in lines:
        indent = len(line) - len(line.lstrip())
        if indent > max_indent:
            max_indent = indent
    if max_indent > 16:  # ~4 níveis com 4 espaços
        smells.append(f"Deep nesting: {max_indent//4} níveis")
    
    # Duplicated code (simplificado: linhas muito similares)
    if len(lines) > 10:
        unique_lines = set(l.strip() for l in lines if l.strip())
        if len(unique_lines) < len(lines) * 0.3:
            smells.append("Possível código duplicado")
    
    return len(smells), smells


def build_lang(file_path: Path, language: str) -> Tuple[bool, str]:
    """
    Compila/testa arquivo conforme linguagem.
    Retorna (success, output).
    """
    if not file_path.exists():
        return False, "Arquivo não encontrado"
    
    if language == "python":
        # Verificar sintaxe Python
        try:
            compile(file_path.read_text(encoding="utf-8"), str(file_path), "exec")
            return True, "Syntax OK"
        except SyntaxError as e:
            return False, f"Syntax error: {e}"
    
    elif language in ["javascript", "typescript"]:
        # Verificar com node (se disponível)
        try:
            result = subprocess.run(
                ["node", "--check", str(file_path)],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0, result.stdout + result.stderr
        except FileNotFoundError:
            return True, "Node não disponível (skipping)"
        except Exception as e:
            return False, f"Erro: {e}"
    
    else:
        # Para outras linguagens, assumir OK
        return True, "Build check skipped (linguagem não suportada)"


def validate_refactoring_order(files: List[Path], action: str = "refatorar") -> Dict[str, Any]:
    """
    Executa validações obrigatórias do Mini-PIN para ordens de refatoração.
    Retorna dicionário com resultados das validações.
    """
    results = {
        "action": action,
        "files_analyzed": len(files),
        "language_profiles": {},
        "archetype_status": {},
        "smells_count": {},
        "build_status": {},
        "profile_pass": True,
        "archetype_pass": True,
        "overall_pass": True,
        "correction_plan": [],
    }
    
    # 1. Gerar language_profile.json
    language_profile = generate_language_profile(files)
    profile_file = TORRE_RELATORIOS / "language_profile.json"
    profile_file.parent.mkdir(parents=True, exist_ok=True)
    profile_file.write_text(json.dumps(language_profile, indent=2, ensure_ascii=False), encoding="utf-8")
    results["language_profile_path"] = str(profile_file.relative_to(REPO_ROOT))
    
    # 2. Para cada arquivo: archetype_check, cross_smells, build_lang
    total_smells = 0
    for file_path in files:
        lang, conf = detect_language(file_path)
        
        # Archetype check
        arch_ok, arch_msg = archetype_check(file_path, lang)
        results["archetype_status"][str(file_path.relative_to(REPO_ROOT))] = {
            "pass": arch_ok,
            "message": arch_msg,
            "language": lang,
            "confidence": conf,
        }
        
        if not arch_ok:
            results["archetype_pass"] = False
            results["correction_plan"].append({
                "file": str(file_path.relative_to(REPO_ROOT)),
                "issue": arch_msg,
                "source": "archetype_check",
            })
        
        # Cross smells
        smells_count, smells_list = cross_smells(file_path)
        total_smells += smells_count
        results["smells_count"][str(file_path.relative_to(REPO_ROOT))] = {
            "count": smells_count,
            "smells": smells_list,
        }
        
        # Build check
        build_ok, build_msg = build_lang(file_path, lang)
        results["build_status"][str(file_path.relative_to(REPO_ROOT))] = {
            "pass": build_ok,
            "message": build_msg,
        }
        
        if not build_ok:
            results["overall_pass"] = False
    
    # 3. Determinar status geral
    if not results["archetype_pass"]:
        results["overall_pass"] = False
    
    # Gerar frase inicial obrigatória
    main_lang = max(language_profile.get("languages", {}).items(), key=lambda x: x[1]["count"], default=("unknown", {}))[0]
    avg_conf = language_profile.get("confidence_avg", {}).get(main_lang, 0.5)
    
    results["mini_pin_status"] = f"Quem age: ENG. Linguagem: {main_lang} (confiança {avg_conf:.2f}). Ação: {action}. Estado: PROFILE={'PASS' if results['profile_pass'] else 'FAIL'}, ARQUETIPO={'PASS' if results['archetype_pass'] else 'FAIL'}, SMELLS={total_smells}."
    
    return results

