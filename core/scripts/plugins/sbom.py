from pathlib import Path


def exists_sbom(sbom_path: Path) -> bool:
    return sbom_path.exists()


