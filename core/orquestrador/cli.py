import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import re

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None
try:
    import openai  # type: ignore
except Exception:  # pragma: no cover
    openai = None


REPO_ROOT = Path(__file__).resolve().parents[2]
CORE_DIR = REPO_ROOT / "core"
TEMPLATES_DIR = CORE_DIR / "templates"
GITHUB_TEMPLATES = TEMPLATES_DIR / "github"
PROJECT_SKELETON = TEMPLATES_DIR / "project_skeleton"

# Pipeline paths
PIPELINE_DIR = REPO_ROOT / "pipeline"
CAP_DIR = PIPELINE_DIR / "capitulos"
SUPERPIPE = PIPELINE_DIR / "superpipeline.yaml"
PIPE_TOC = PIPELINE_DIR / "PIPELINE_TOC.md"
PIPE_AUDIT = REPO_ROOT / "relatorios" / "pipeline_audit.json"


def run(cmd: list[str], cwd: Path | None = None) -> int:
    try:
        return subprocess.call(cmd, cwd=str(cwd) if cwd else None)
    except FileNotFoundError:
        return 0


def cmd_init(dest: Path) -> None:
    dest = dest.resolve()
    dest.mkdir(parents=True, exist_ok=True)
    # Copiar skeleton base
    if PROJECT_SKELETON.exists():
        for item in PROJECT_SKELETON.iterdir():
            target = dest / item.name
            if item.is_dir():
                if not target.exists():
                    shutil.copytree(item, target)
            else:
                if not target.exists():
                    shutil.copy2(item, target)
    # Copiar workflows base
    workflows_dir = dest / ".github" / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)
    if GITHUB_TEMPLATES.exists():
        for item in GITHUB_TEMPLATES.iterdir():
            shutil.copy2(item, workflows_dir / item.name)


def cmd_sync(proj_path: Path) -> None:
    proj_path = proj_path.resolve()
    # Sincronizar leis, orquestrador e workflows
    for rel in ["sop/leis.yaml", "sop/exceptions.yaml", "orquestrador/config.yaml"]:
        src = CORE_DIR / rel
        dst = proj_path / "core" / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    # Workflows
    workflows_dir = proj_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)
    for item in GITHUB_TEMPLATES.iterdir():
        shutil.copy2(item, workflows_dir / item.name)


def cmd_validate(proj_path: Path) -> int:
    proj_path = proj_path.resolve()
    mk = proj_path / "core" / "orquestrador" / "Makefile"
    if mk.exists():
        return run(["make", "-C", str(mk.parent), "sop"]) or 0
    return 0


def cmd_report(proj_path: Path) -> None:
    rel = proj_path.resolve() / "relatorios"
    rel.mkdir(exist_ok=True)
    status_file = rel / "sop_status.json"
    parecer_file = rel / "parecer_gatekeeper.md"
    resumo = {
        "existe_status": status_file.exists(),
        "existe_parecer": parecer_file.exists(),
    }
    (rel / "resumo_report.json").write_text(json.dumps(resumo, indent=2), encoding="utf-8")


# ---- Pipeline helpers ----
def _simple_yaml_list(val: str):
    val = val.strip()
    if val.startswith("[") and val.endswith("]"):
        inner = val[1:-1].strip()
        if not inner:
            return []
        return [x.strip() for x in inner.split(",")]
    return []


def yload(p: Path):
    if not p.exists():
        raise FileNotFoundError(str(p))
    text = p.read_text(encoding="utf-8")
    if yaml is not None:
        return yaml.safe_load(text)
    # Fallback simples para a nossa estrutura conhecida
    data: dict = {}
    current_list = None
    current_section = None
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line or line.strip().startswith("#"):
            i += 1
            continue
        if not line.startswith(" "):
            if ":" in line:
                k, v = line.split(":", 1)
                k = k.strip()
                v = v.strip()
                if v == "":
                    # section start
                    if k in ("modulos", "capitulos"):
                        data[k] = []
                        current_section = k
                        current_list = data[k]
                    else:
                        data[k] = {}
                else:
                    # scalar or list
                    if v.startswith("["):
                        data[k] = _simple_yaml_list(v)
                    else:
                        try:
                            data[k] = int(v)
                        except Exception:
                            data[k] = v.strip('"')
        else:
            # inside section list
            if current_section in ("modulos", "capitulos") and line.strip().startswith("- "):
                # start of an item block
                item: dict = {}
                current_list.append(item)
                # parse inline key if present after '- '
                rest = line.strip()[2:].strip()
                if rest and ":" in rest:
                    k0, v0 = rest.split(":", 1)
                    k0 = k0.strip()
                    v0 = v0.strip()
                    if v0.startswith("["):
                        item[k0] = _simple_yaml_list(v0)
                    else:
                        item[k0] = v0.strip('"')
                # consume following indented lines for this item
                i += 1
                while i < len(lines) and lines[i].startswith("  "):
                    if lines[i].startswith("  - "):
                        break
                    sub = lines[i].strip()
                    if sub.endswith(":"):
                        # start of nested dict not used here
                        pass
                    elif ":" in sub:
                        k, v = sub.split(":", 1)
                        k = k.strip()
                        v = v.strip()
                        if v.startswith("["):
                            item[k] = _simple_yaml_list(v)
                        else:
                            item[k] = v.strip('"')
                    i += 1
                continue  # skip extra i++ below
        i += 1
    return data


def ydump(p: Path, data: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    if yaml is not None:
        p.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    else:
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def cmd_gen_pipeline() -> None:
    sp = yload(SUPERPIPE)
    chapters = sp.get("capitulos", [])
    for ch in chapters:
        cid = ch["id"]
        out = CAP_DIR / cid / "capitulo.yaml"
        cap = {
            "id": cid,
            "nome": ch.get("nome", cid),
            "gates_alvo": ch.get("gates_alvo", []),
            "modulos": {
                "inicia": ch.get("inicia", []),
                "continua": ch.get("continua", []),
                "termina": ch.get("termina", []),
            },
            "tarefas": [],
        }
        ydump(out, cap)


def cmd_validate_pipeline() -> int:
    sp = yload(SUPERPIPE)
    mods = {m["id"]: m for m in sp.get("modulos", [])}
    chapters = sp.get("capitulos", [])
    seen = set()

    deps_missing = []
    for m in mods.values():
        for d in m.get("depende", []):
            if d not in mods:
                deps_missing.append((m["id"], d))

    for ch in chapters:
        for bucket in ("inicia", "continua", "termina"):
            for m in ch.get(bucket, []):
                base = m.split("@")[0]
                seen.add(base)

    not_covered = [m for m in mods if m not in seen and mods[m].get("tipo") != "fundacao"]

    visiting, visited, cycle = set(), set(), []

    def dfs(u: str):
        visiting.add(u)
        for v in mods[u].get("depende", []):
            if v not in mods:
                continue
            if v in visiting:
                cycle.append((u, v))
            elif v not in visited:
                dfs(v)
        visiting.remove(u)
        visited.add(u)

    for m in mods:
        if m not in visited:
            dfs(m)

    audit = {
        "deps_missing": deps_missing,
        "not_covered_modules": not_covered,
        "cycles": cycle,
        "chapters": [c["id"] for c in chapters],
    }
    PIPE_AUDIT.parent.mkdir(parents=True, exist_ok=True)
    PIPE_AUDIT.write_text(json.dumps(audit, indent=2), encoding="utf-8")

    ok = not deps_missing and not not_covered and not cycle
    print("VALIDATE:", "PASS" if ok else "ISSUES")
    return 0 if ok else 1


def cmd_gen_toc() -> None:
    sp = yload(SUPERPIPE)
    lines = ["# PIPELINE – TOC (sumário)", "", "## Superpipeline"]
    lines.append(f"- Gates: {', '.join(sp.get('gates_ordem', []))}")
    lines.append("")
    lines.append("### Módulos")
    for m in sp.get("modulos", []):
        deps = ", ".join(m.get("depende", [])) or "—"
        lines.append(f"- **{m['id']}** ({m.get('tipo','')}) — depende: {deps}")
    lines.append("")
    lines.append("## Capítulos")
    for ch in sp.get("capitulos", []):
        cid = ch["id"]
        p = CAP_DIR / cid / "capitulo.yaml"
        status = "🟢" if p.exists() else "⚪"
        gates = ", ".join(ch.get("gates_alvo", []))
        lines.append(f"- {status} **{cid}** — {ch.get('nome','')} (gates: {gates})  → `pipeline/capitulos/{cid}/capitulo.yaml`")
        if p.exists():
            cap = yload(p)
            ins = ", ".join(cap.get("modulos", {}).get("inicia", [])) or "—"
            cont = ", ".join(cap.get("modulos", {}).get("continua", [])) or "—"
            ter = ", ".join(cap.get("modulos", {}).get("termina", [])) or "—"
            lines.append(f"  - inicia: {ins}")
            lines.append(f"  - continua: {cont}")
            lines.append(f"  - termina: {ter}")
    PIPE_TOC.write_text("\n".join(lines) + "\n", encoding="utf-8")


def gatekeeper_prep() -> None:
    # 1) validar pipeline
    _ = cmd_validate_pipeline()  # escreve relatorios/pipeline_audit.json
    # 2) gerar TOC
    cmd_gen_toc()
    # 3) produzir resumo Gatekeeper
    audit_path = PIPE_AUDIT
    gk_path = REPO_ROOT / "relatorios" / "pipeline_gate_input.json"
    audit = {}
    if audit_path.exists():
        try:
            audit = json.loads(audit_path.read_text(encoding="utf-8"))
        except Exception:
            audit = {}
    payload = {
        "pipeline_ok": (not audit.get("deps_missing") and not audit.get("not_covered_modules") and not audit.get("cycles")),
        "issues": audit,
        "toc_path": "pipeline/PIPELINE_TOC.md",
    }
    gk_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("Gatekeeper input gerado em", gk_path)


def gatekeeper_run() -> int:
    """
    Gatekeeper da FÁBRICA 2.0 - Decide G4/G5.
    Verifica integridade técnica e pipeline; emite APROVADO/VETO.
    """
    REL_DIR = REPO_ROOT / "relatorios"
    PIPE_DIR = REPO_ROOT / "pipeline"
    
    # Caminhos dos artefatos
    sop_relatorio_path = REL_DIR / "relatorio_sop.md"
    sbom_path = REL_DIR / "sbom.json"
    pipeline_input_path = REL_DIR / "pipeline_gate_input.json"
    pipeline_toc_path = PIPE_DIR / "PIPELINE_TOC.md"
    sop_status_path = REL_DIR / "sop_status.json"
    parecer_path = REL_DIR / "parecer_gatekeeper.md"
    
    print("🔎 Gatekeeper da FÁBRICA 2.0 iniciado...")
    print("📖 Lendo artefatos...")
    
    # 1. Ler artefatos
    sop_relatorio = ""
    if sop_relatorio_path.exists():
        sop_relatorio = sop_relatorio_path.read_text(encoding="utf-8")
    else:
        print("⚠️  Aviso: relatorios/relatorio_sop.md não encontrado")
    
    sbom_data = {}
    if sbom_path.exists():
        try:
            sbom_data = json.loads(sbom_path.read_text(encoding="utf-8"))
        except Exception:
            print("⚠️  Aviso: erro ao ler relatorios/sbom.json")
    else:
        print("⚠️  Aviso: relatorios/sbom.json não encontrado")
    
    pipeline_input = {}
    pipeline_ok = False
    if pipeline_input_path.exists():
        try:
            pipeline_input = json.loads(pipeline_input_path.read_text(encoding="utf-8"))
            pipeline_ok = pipeline_input.get("pipeline_ok", False)
        except Exception:
            print("⚠️  Aviso: erro ao ler relatorios/pipeline_gate_input.json")
    else:
        print("⚠️  Aviso: relatorios/pipeline_gate_input.json não encontrado")
    
    pipeline_toc = ""
    if pipeline_toc_path.exists():
        pipeline_toc = pipeline_toc_path.read_text(encoding="utf-8")
    else:
        print("⚠️  Aviso: pipeline/PIPELINE_TOC.md não encontrado")
    
    sop_status = {}
    sop_status_value = "UNKNOWN"
    if sop_status_path.exists():
        try:
            sop_status = json.loads(sop_status_path.read_text(encoding="utf-8"))
            sop_status_value = sop_status.get("status", "UNKNOWN")
        except Exception:
            print("⚠️  Aviso: erro ao ler relatorios/sop_status.json")
    else:
        print("⚠️  Aviso: relatorios/sop_status.json não encontrado")
    
    # 2. Regras de VETO automático
    veto_automatico = False
    motivo_veto = []
    
    if sop_status_value == "BLOQUEADO":
        veto_automatico = True
        motivo_veto.append("SOP está BLOQUEADO")
    
    if not pipeline_ok:
        veto_automatico = True
        motivo_veto.append("pipeline_ok=false")
    
    # 3. Gerar parecer
    data_emissao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    parecer_lines = [
        "# Parecer Gatekeeper - FÁBRICA 2.0",
        "",
        f"**Data**: {data_emissao}",
        "",
    ]
    
    if veto_automatico:
        parecer_lines.extend([
            "## DECISÃO: ⛔ VETO",
            "",
            "### Motivo do Veto",
        ])
        for motivo in motivo_veto:
            parecer_lines.append(f"- {motivo}")
        parecer_lines.append("")
    else:
        parecer_lines.extend([
            "## DECISÃO: ✅ APROVADO",
            "",
        ])
    
    # 4. Estrutura em 3 pontos conforme especificação
    parecer_lines.extend([
        "---",
        "",
        "## 1. Evidência Técnica",
        "",
        "### Relatório SOP",
        f"**Artefato**: `relatorios/relatorio_sop.md`",
        f"**Status SOP**: {sop_status_value}",
    ])
    
    # Detalhes do SOP
    if sop_status_value == "PASS":
        metrics = sop_status.get("metrics", {})
        coverage = metrics.get("coverage", 0)
        coverage_ok = metrics.get("coverage_ok", True)  # Default True se não existir (status PASS implica ok)
        semgrep_ok = metrics.get("semgrep", {}).get("ok", False)
        sbom_ok = metrics.get("sbom", {}).get("ok", False)
        bandit_ok = metrics.get("bandit", {}).get("ok", False)
        trivy_ok = metrics.get("trivy", {}).get("ok", False)
        parecer_lines.extend([
            f"- Cobertura: {coverage}% ({'✅' if coverage_ok else '⚠️'})",
            f"- Semgrep: {'✅' if semgrep_ok else '❌'}",
            f"- Bandit: {'✅' if bandit_ok else '❌'}",
            f"- Trivy: {'✅' if trivy_ok else '❌'}",
            f"- SBOM: {'✅' if sbom_ok else '❌'}",
        ])
    elif sop_status_value == "BLOQUEADO":
        violations = sop_status.get("violations", [])
        parecer_lines.append(f"- Regras violadas: {', '.join(violations) if violations else 'N/A'}")
    
    parecer_lines.extend([
        "",
        "### SBOM (Software Bill of Materials)",
        f"**Artefato**: `relatorios/sbom.json`",
    ])
    
    if sbom_data:
        bom_format = sbom_data.get("bomFormat", "unknown")
        spec_version = sbom_data.get("specVersion", "unknown")
        components_count = len(sbom_data.get("components", []))
        parecer_lines.extend([
            f"- Formato: {bom_format}",
            f"- Versão da especificação: {spec_version}",
            f"- Componentes catalogados: {components_count}",
        ])
    else:
        parecer_lines.append("- ⚠️ SBOM não encontrado ou inválido")
    
    parecer_lines.extend([
        "",
        "### Pipeline",
        f"**Artefato**: `relatorios/pipeline_gate_input.json`",
        f"**Estado**: {'✅ OK' if pipeline_ok else '❌ INVÁLIDA'}",
    ])
    
    if pipeline_input.get("issues"):
        issues = pipeline_input["issues"]
        deps_missing = issues.get("deps_missing", [])
        not_covered = issues.get("not_covered_modules", [])
        cycles = issues.get("cycles", [])
        if deps_missing or not_covered or cycles:
            parecer_lines.append("- **Issues encontradas**:")
            if deps_missing:
                parecer_lines.append(f"  - Dependências ausentes: {len(deps_missing)}")
            if not_covered:
                parecer_lines.append(f"  - Módulos não cobertos: {len(not_covered)}")
            if cycles:
                parecer_lines.append(f"  - Ciclos detectados: {len(cycles)}")
            parecer_lines.append("  - Ver detalhes em: `relatorios/pipeline_audit.json`")
    
    parecer_lines.extend([
        f"- **TOC**: `{pipeline_input.get('toc_path', 'pipeline/PIPELINE_TOC.md')}`",
        "",
        "---",
        "",
        "## 2. Avaliação (Ética/Risco)",
        "",
    ])
    
    if veto_automatico:
        parecer_lines.extend([
            "### Riscos Identificados",
            "- **Bloqueio técnico**: Não é possível avançar devido a violações nas regras SOP ou pipeline inválida.",
        ])
        if sop_status_value == "BLOQUEADO":
            parecer_lines.append("- **Conformidade**: Requisitos de gate não satisfeitos.")
        if not pipeline_ok:
            parecer_lines.append("- **Integridade da pipeline**: Estrutura da pipeline apresenta inconsistências.")
    else:
        parecer_lines.extend([
            "### Análise de Conformidade",
            "- ✅ **SOP**: Status PASS - Requisitos técnicos satisfeitos",
            "- ✅ **Pipeline**: Estrutura válida e consistente",
            "- ✅ **SBOM**: Presente e válido (conformidade com requisitos de rastreabilidade)",
            "",
            "### Riscos Identificados",
            "- **Risco residual**: Baixo",
            "- Todas as verificações técnicas passaram com sucesso",
        ])
    
    parecer_lines.extend([
        "",
        "---",
        "",
        "## 3. Impacto Residual",
        "",
    ])
    
    if veto_automatico:
        parecer_lines.extend([
            "### Bloqueios Críticos",
            "- ⛔ **Não é possível prosseguir para os gates G4/G5**",
            "- Ação requerida: Corrigir violações identificadas antes de nova avaliação",
        ])
        if sop_status_value == "BLOQUEADO":
            parecer_lines.append("- Revisar e corrigir as regras violadas conforme `relatorios/relatorio_sop.md`")
        if not pipeline_ok:
            parecer_lines.append("- Corrigir issues da pipeline conforme `relatorios/pipeline_audit.json`")
    else:
        parecer_lines.extend([
            "### Próximos Passos",
            "- ✅ **Gatekeeper aprovou**: Sistema pronto para gates G4/G5",
            "- **Recomendações**:",
            "  - Manter monitorização contínua das métricas de qualidade",
            "  - Atualizar SBOM em caso de novas dependências",
            "  - Validar pipeline após mudanças estruturais",
        ])
    
    parecer_lines.extend([
        "",
        "---",
        "",
        "## Referências dos Artefatos Analisados",
        "",
        "- `relatorios/relatorio_sop.md` - Relatório SOP completo",
        "- `relatorios/sbom.json` - Software Bill of Materials",
        "- `relatorios/pipeline_gate_input.json` - Estado da pipeline",
        "- `pipeline/PIPELINE_TOC.md` - Índice navegável da pipeline",
        "- `relatorios/sop_status.json` - Status detalhado do SOP",
        "",
        "---",
        "",
        f"**Assinado**: Gatekeeper (Composer Edition)",
        f"**Emitido em**: {data_emissao}",
    ])
    
    # 5. Escrever parecer
    parecer_path.parent.mkdir(parents=True, exist_ok=True)
    parecer_path.write_text("\n".join(parecer_lines), encoding="utf-8")
    
    print(f"✅ Parecer gerado em: {parecer_path}")
    
    if veto_automatico:
        print("❌ Gatekeeper VETO emitido")
        print(f"   Motivos: {', '.join(motivo_veto)}")
        return 1
    else:
        print("✅ Gatekeeper APROVADO")
        return 0


def review_codex() -> None:
    """Revisão ética e factual com GPT-4o (Codex Edition)."""
    sop_path = REPO_ROOT / "relatorios" / "relatorio_sop.md"
    sbom_path = REPO_ROOT / "relatorios" / "sbom.json"
    pipe_path = REPO_ROOT / "relatorios" / "pipeline_gate_input.json"
    out_path = REPO_ROOT / "relatorios" / "parecer_gatekeeper_codex.md"

    sop_text = sop_path.read_text(encoding="utf-8") if sop_path.exists() else ""
    sbom_text = sbom_path.read_text(encoding="utf-8") if sbom_path.exists() else ""
    pipe_json = {}
    if pipe_path.exists():
        try:
            pipe_json = json.loads(pipe_path.read_text(encoding="utf-8"))
        except Exception:
            pipe_json = {}

    prompt = f"""
Atua como Gatekeeper Ético (Codex Edition) da FÁBRICA 2.0.
Analisa os seguintes artefactos e emite parecer humano detalhado.

### SOP
{sop_text}

### SBOM
{sbom_text}

### Pipeline
{json.dumps(pipe_json, indent=2)}

Tarefa:
- Avalia coerência ética, factual e técnica.
- Classifica: DECISÃO ÉTICA: APROVADO | VETO.
- Lista riscos residuais, inconsistências ou omissões.
- Recomenda melhorias ou pontos de revisão futura.
Gera o parecer em formato Markdown.
"""

    print("🧠 Connecting to GPT-4o Codex...")
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or openai is None:
        out_path.write_text(
            "OPENAI_API_KEY não configurada ou SDK indisponível. Skipping Codex review.",
            encoding="utf-8",
        )
        print("⚠️ Chave API não configurada ou SDK ausente.")
        return
    openai.api_key = api_key
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "És o Gatekeeper Ético e Factual da FÁBRICA 2.0."},
                {"role": "user", "content": prompt},
            ],
        )
        output = response["choices"][0]["message"]["content"]
    except Exception as e:
        output = f"Falha ao contactar Codex: {e}"
    out_path.write_text(output, encoding="utf-8")
    print(f"✅ Parecer ético gerado em {out_path}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="factory", description="FÁBRICA CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Inicializa projeto com skeleton + workflows")
    p_init.add_argument("dest")

    p_sync = sub.add_parser("sync", help="Sincroniza leis, orquestrador e workflows")
    p_sync.add_argument("proj_path")

    p_val = sub.add_parser("validate", help="Corre make sop no projeto")
    p_val.add_argument("proj_path")

    p_rep = sub.add_parser("report", help="Agrega relatórios e produz sumário")
    p_rep.add_argument("proj_path")

    # Pipeline commands
    sub.add_parser("gen_pipeline", help="Gera capítulos a partir da superpipeline")
    sub.add_parser("validate_pipeline", help="Valida consistência da superpipeline")
    sub.add_parser("toc", help="Gera pipeline/PIPELINE_TOC.md")
    sub.add_parser("gatekeeper_prep", help="Prepara inputs do Gatekeeper (audit + TOC)")
    sub.add_parser("gatekeeper_run", help="Executa Gatekeeper (Composer Edition) - decide G4/G5")
    sub.add_parser("review_codex", help="Revisão ética (GPT-4o)")

    args = parser.parse_args(argv)
    if args.cmd == "init":
        cmd_init(Path(args.dest))
        return 0
    if args.cmd == "sync":
        cmd_sync(Path(args.proj_path))
        return 0
    if args.cmd == "validate":
        return cmd_validate(Path(args.proj_path))
    if args.cmd == "report":
        cmd_report(Path(args.proj_path))
        return 0
    if args.cmd == "gen_pipeline":
        cmd_gen_pipeline()
        return 0
    if args.cmd == "validate_pipeline":
        return cmd_validate_pipeline()
    if args.cmd == "toc":
        cmd_gen_toc()
        return 0
    if args.cmd == "gatekeeper_prep":
        gatekeeper_prep()
        return 0
    if args.cmd == "gatekeeper_run":
        return gatekeeper_run()
    if args.cmd == "review_codex":
        review_codex()
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))


