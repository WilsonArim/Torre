import argparse
import json
import os
import shutil
import subprocess
import sys
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
    if args.cmd == "review_codex":
        review_codex()
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))


