from __future__ import annotations
import json, re, subprocess
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class Vulnerability:
    """Informação sobre vulnerabilidade"""
    id: str
    severity: str  # "low", "medium", "high", "critical"
    description: str
    package: str
    version: str
    cve_id: Optional[str]
    advisory_url: Optional[str]

@dataclass
class PackageInfo:
    """Informação sobre pacote"""
    name: str
    version: str
    license: Optional[str]
    vulnerabilities: List[Vulnerability]

class SCAScanner:
    """
    Scanner SCA/SBOM leve (Semgrep/OSV) como advisory
    Objetivo: detecção de vulnerabilidades sem bloquear fluxo
    """
    
    def __init__(self):
        self.supported_languages = ["python", "javascript", "typescript", "go", "rust"]
        self.severity_weights = {
            "low": 0.1,
            "medium": 0.3,
            "high": 0.6,
            "critical": 1.0
        }
    
    def scan_dependencies(self, project_path: str) -> Dict[str, Any]:
        """Escaneia dependências do projeto"""
        scan_result = {
            "packages": [],
            "vulnerabilities": [],
            "risk_score": 0.0,
            "total_packages": 0,
            "vulnerable_packages": 0
        }
        
        # Detecta tipo de projeto
        project_type = self._detect_project_type(project_path)
        
        if project_type == "python":
            scan_result.update(self._scan_python_dependencies(project_path))
        elif project_type in ["javascript", "typescript"]:
            scan_result.update(self._scan_js_dependencies(project_path))
        elif project_type == "go":
            scan_result.update(self._scan_go_dependencies(project_path))
        elif project_type == "rust":
            scan_result.update(self._scan_rust_dependencies(project_path))
        
        # Calcula score de risco
        scan_result["risk_score"] = self._calculate_risk_score(scan_result["vulnerabilities"])
        
        return scan_result
    
    def _detect_project_type(self, project_path: str) -> str:
        """Detecta tipo de projeto baseado em ficheiros"""
        import pathlib
        
        project_files = list(pathlib.Path(project_path).glob("*"))
        file_names = [f.name.lower() for f in project_files if f.is_file()]
        
        if any(name in file_names for name in ["requirements.txt", "pyproject.toml", "setup.py"]):
            return "python"
        elif any(name in file_names for name in ["package.json", "yarn.lock", "pnpm-lock.yaml"]):
            return "javascript"
        elif any(name in file_names for name in ["go.mod", "go.sum"]):
            return "go"
        elif any(name in file_names for name in ["Cargo.toml", "Cargo.lock"]):
            return "rust"
        
        return "unknown"
    
    def _scan_python_dependencies(self, project_path: str) -> Dict[str, Any]:
        """Escaneia dependências Python"""
        result = {
            "packages": [],
            "vulnerabilities": [],
            "total_packages": 0,
            "vulnerable_packages": 0
        }
        
        try:
            # Tenta usar pip list
            output = subprocess.run(
                ["pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                cwd=project_path
            )
            
            if output.returncode == 0:
                packages = json.loads(output.stdout)
                result["total_packages"] = len(packages)
                
                for pkg in packages:
                    package_info = PackageInfo(
                        name=pkg["name"],
                        version=pkg["version"],
                        license=None,
                        vulnerabilities=[]
                    )
                    result["packages"].append(package_info)
                    
                    # Simula vulnerabilidades conhecidas (em produção, usar API real)
                    vulns = self._check_python_vulnerabilities(pkg["name"], pkg["version"])
                    if vulns:
                        package_info.vulnerabilities = vulns
                        result["vulnerabilities"].extend(vulns)
                        result["vulnerable_packages"] += 1
        
        except Exception as e:
            print(f"⚠️ Erro ao escanear Python: {e}")
        
        return result
    
    def _scan_js_dependencies(self, project_path: str) -> Dict[str, Any]:
        """Escaneia dependências JavaScript/TypeScript"""
        result = {
            "packages": [],
            "vulnerabilities": [],
            "total_packages": 0,
            "vulnerable_packages": 0
        }
        
        try:
            # Tenta usar npm audit
            output = subprocess.run(
                ["npm", "audit", "--json"],
                capture_output=True,
                text=True,
                cwd=project_path
            )
            
            if output.returncode == 0:
                audit_data = json.loads(output.stdout)
                
                if "vulnerabilities" in audit_data:
                    for pkg_name, vuln_data in audit_data["vulnerabilities"].items():
                        for vuln in vuln_data.get("via", []):
                            if isinstance(vuln, dict) and "title" in vuln:
                                vulnerability = Vulnerability(
                                    id=vuln.get("id", "unknown"),
                                    severity=vuln.get("severity", "medium"),
                                    description=vuln.get("title", ""),
                                    package=pkg_name,
                                    version=vuln_data.get("version", "unknown"),
                                    cve_id=vuln.get("cve", None),
                                    advisory_url=vuln.get("url", None)
                                )
                                result["vulnerabilities"].append(vulnerability)
        
        except Exception as e:
            print(f"⚠️ Erro ao escanear JS: {e}")
        
        return result
    
    def _scan_go_dependencies(self, project_path: str) -> Dict[str, Any]:
        """Escaneia dependências Go"""
        result = {
            "packages": [],
            "vulnerabilities": [],
            "total_packages": 0,
            "vulnerable_packages": 0
        }
        
        try:
            # Tenta usar go list
            output = subprocess.run(
                ["go", "list", "-m", "all"],
                capture_output=True,
                text=True,
                cwd=project_path
            )
            
            if output.returncode == 0:
                lines = output.stdout.strip().split('\n')
                result["total_packages"] = len(lines)
                
                for line in lines:
                    if ' ' in line:
                        name, version = line.rsplit(' ', 1)
                        package_info = PackageInfo(
                            name=name,
                            version=version,
                            license=None,
                            vulnerabilities=[]
                        )
                        result["packages"].append(package_info)
        
        except Exception as e:
            print(f"⚠️ Erro ao escanear Go: {e}")
        
        return result
    
    def _scan_rust_dependencies(self, project_path: str) -> Dict[str, Any]:
        """Escaneia dependências Rust"""
        result = {
            "packages": [],
            "vulnerabilities": [],
            "total_packages": 0,
            "vulnerable_packages": 0
        }
        
        try:
            # Tenta usar cargo audit
            output = subprocess.run(
                ["cargo", "audit", "--json"],
                capture_output=True,
                text=True,
                cwd=project_path
            )
            
            if output.returncode == 0:
                audit_data = json.loads(output.stdout)
                
                if "vulnerabilities" in audit_data:
                    for vuln in audit_data["vulnerabilities"]:
                        vulnerability = Vulnerability(
                            id=vuln.get("id", "unknown"),
                            severity=vuln.get("severity", "medium"),
                            description=vuln.get("description", ""),
                            package=vuln.get("package", "unknown"),
                            version=vuln.get("version", "unknown"),
                            cve_id=vuln.get("cve", None),
                            advisory_url=vuln.get("advisory", {}).get("url", None)
                        )
                        result["vulnerabilities"].append(vulnerability)
        
        except Exception as e:
            print(f"⚠️ Erro ao escanear Rust: {e}")
        
        return result
    
    def _check_python_vulnerabilities(self, package_name: str, version: str) -> List[Vulnerability]:
        """Verifica vulnerabilidades Python (simulado)"""
        # Em produção, usar API real (OSV, NVD, etc.)
        known_vulns = {
            "requests": {
                "2.28.0": [
                    Vulnerability(
                        id="CVE-2023-32681",
                        severity="high",
                        description="HTTP header injection vulnerability",
                        package="requests",
                        version="2.28.0",
                        cve_id="CVE-2023-32681",
                        advisory_url="https://nvd.nist.gov/vuln/detail/CVE-2023-32681"
                    )
                ]
            },
            "urllib3": {
                "1.26.0": [
                    Vulnerability(
                        id="CVE-2023-24329",
                        severity="medium",
                        description="CRLF injection vulnerability",
                        package="urllib3",
                        version="1.26.0",
                        cve_id="CVE-2023-24329",
                        advisory_url="https://nvd.nist.gov/vuln/detail/CVE-2023-24329"
                    )
                ]
            }
        }
        
        return known_vulns.get(package_name, {}).get(version, [])
    
    def _calculate_risk_score(self, vulnerabilities: List[Vulnerability]) -> float:
        """Calcula score de risco baseado em vulnerabilidades"""
        if not vulnerabilities:
            return 0.0
        
        total_weight = 0.0
        for vuln in vulnerabilities:
            weight = self.severity_weights.get(vuln.severity, 0.3)
            total_weight += weight
        
        # Normaliza para 0-1
        return min(1.0, total_weight / len(vulnerabilities))
    
    def generate_advisory_report(self, scan_result: Dict[str, Any]) -> str:
        """Gera relatório de advisory"""
        report = ["# Relatório SCA/SBOM - Advisory\n"]
        
        report.append(f"## Resumo")
        report.append(f"- **Total de pacotes**: {scan_result['total_packages']}")
        report.append(f"- **Pacotes vulneráveis**: {scan_result['vulnerable_packages']}")
        report.append(f"- **Score de risco**: {scan_result['risk_score']:.2f}")
        report.append("")
        
        if scan_result["vulnerabilities"]:
            report.append("## Vulnerabilidades Encontradas")
            
            # Agrupa por severidade
            by_severity = {}
            for vuln in scan_result["vulnerabilities"]:
                severity = vuln.severity
                if severity not in by_severity:
                    by_severity[severity] = []
                by_severity[severity].append(vuln)
            
            for severity in ["critical", "high", "medium", "low"]:
                if severity in by_severity:
                    report.append(f"### {severity.upper()}")
                    for vuln in by_severity[severity][:5]:  # Top 5 por severidade
                        report.append(f"- **{vuln.package}@{vuln.version}**: {vuln.description}")
                        if vuln.cve_id:
                            report.append(f"  - CVE: {vuln.cve_id}")
                        if vuln.advisory_url:
                            report.append(f"  - Advisory: {vuln.advisory_url}")
                        report.append("")
        else:
            report.append("## Status")
            report.append("✅ Nenhuma vulnerabilidade conhecida encontrada.")
        
        report.append("## Recomendações")
        if scan_result["risk_score"] > 0.7:
            report.append("- ⚠️ **Alto risco**: Considerar atualização imediata de dependências")
        elif scan_result["risk_score"] > 0.3:
            report.append("- ⚠️ **Risco médio**: Planejar atualizações de segurança")
        else:
            report.append("- ✅ **Baixo risco**: Manter dependências atualizadas")
        
        return "\n".join(report)
    
    def should_block_merge(self, scan_result: Dict[str, Any], threshold: float = 0.8) -> bool:
        """Decide se deve bloquear merge baseado no score de risco"""
        return scan_result["risk_score"] > threshold
