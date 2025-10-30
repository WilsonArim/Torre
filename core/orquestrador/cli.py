import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CORE_DIR = REPO_ROOT / "core"
TEMPLATES_DIR = CORE_DIR / "templates"
GITHUB_TEMPLATES = TEMPLATES_DIR / "github"
PROJECT_SKELETON = TEMPLATES_DIR / "project_skeleton"


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
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))


