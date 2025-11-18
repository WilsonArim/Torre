from pathlib import Path

try:
    from defusedxml import ElementTree as ET  # type: ignore
except ImportError:  # pragma: no cover
    raise ImportError("defusedxml é obrigatório para parsing seguro de coverage XML")


def read_coverage_percent(coverage_xml: Path) -> float:
    if not coverage_xml.exists():
        return 0.0
    try:
        tree = ET.parse(str(coverage_xml))
        rate = tree.getroot().attrib.get("line-rate")
        if rate is None:
            return 0.0
        return round(float(rate) * 100, 2)
    except Exception:
        return 0.0


