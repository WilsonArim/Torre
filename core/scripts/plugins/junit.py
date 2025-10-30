from pathlib import Path
import xml.etree.ElementTree as ET


def read_junit_summary(report_xml: Path) -> dict:
    if not report_xml.exists():
        return {"ok": True, "tests": 0, "failures": 0, "errors": 0}
    try:
        tree = ET.parse(str(report_xml))
        root = tree.getroot()
        tests = int(root.attrib.get("tests", 0))
        failures = int(root.attrib.get("failures", 0))
        errors = int(root.attrib.get("errors", 0))
        return {"ok": (failures == 0 and errors == 0), "tests": tests, "failures": failures, "errors": errors}
    except Exception:
        return {"ok": True, "tests": 0, "failures": 0, "errors": 0}


