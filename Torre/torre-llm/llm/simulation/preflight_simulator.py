from __future__ import annotations
import subprocess, tempfile, pathlib, re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

def assess_refactor_plan(plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Avalia rapidamente se o plano é executável:
      - existe pelo menos 1 ação
      - provas (commands) estão presentes
    Não executa nada (read-only). Retorna 'advisory_ok' e 'reasons'.
    """
    reasons: List[str] = []
    if not plan or plan.get("mode") != "ADVISORY":
        reasons.append("plan-not-advisory")
    if not plan.get("actions"):
        reasons.append("no-actions")
    if not plan.get("proofs"):
        reasons.append("no-proofs")
    ok = len(reasons) == 0
    return {"advisory_ok": ok, "reasons": reasons}

@dataclass
class PreflightCheck:
    """Resultado de um check individual"""
    name: str
    passed: bool
    details: str
    duration_ms: int

@dataclass
class PreflightResult:
    """Resultado completo do preflight"""
    preflight_ok: bool
    failing_checks: List[str]
    est_ttg_ms: int
    impacted_modules: List[str]
    coverage_delta: float
    checks: List[PreflightCheck]

class PreflightSimulator:
    """
    Preflight Impact Simulator: simula impacto do patch sem alterar o repo
    Objetivo: validação pré-apply com checks incrementais
    """
    
    def __init__(self):
        self.check_timeout = 30  # segundos por check
        self.required_checks = [
            "git_apply_check",
            "typecheck_incremental",
            "lint_incremental",
            "test_selection",
            "perf_sentinels",
            "secret_scan"
        ]
    
    def simulate_preflight(self, 
                          diff: str,
                          changed_files: List[str],
                          graph: Dict[str, Any]) -> PreflightResult:
        """Executa simulação completa do preflight"""
        
        checks = []
        failing_checks = []
        
        # 1. Git apply check
        git_check = self._check_git_apply(diff)
        checks.append(git_check)
        if not git_check.passed:
            failing_checks.append(git_check.name)
        
        # 2. Typecheck incremental
        typecheck = self._check_typecheck_incremental(changed_files)
        checks.append(typecheck)
        if not typecheck.passed:
            failing_checks.append(typecheck.name)
        
        # 3. Lint incremental
        lint_check = self._check_lint_incremental(changed_files)
        checks.append(lint_check)
        if not lint_check.passed:
            failing_checks.append(lint_check.name)
        
        # 4. Test selection
        test_check = self._check_test_selection(changed_files, graph)
        checks.append(test_check)
        if not test_check.passed:
            failing_checks.append(test_check.name)
        
        # 5. Performance sentinels
        perf_check = self._check_perf_sentinels(changed_files)
        checks.append(perf_check)
        if not perf_check.passed:
            failing_checks.append(perf_check.name)
        
        # 6. Secret scan
        secret_check = self._check_secret_scan(diff)
        checks.append(secret_check)
        if not secret_check.passed:
            failing_checks.append(secret_check.name)
        
        # Calcula resultados agregados
        preflight_ok = len(failing_checks) == 0
        est_ttg_ms = self._estimate_ttg(checks)
        impacted_modules = self._identify_impacted_modules(changed_files, graph)
        coverage_delta = self._estimate_coverage_delta(changed_files, graph)
        
        return PreflightResult(
            preflight_ok=preflight_ok,
            failing_checks=failing_checks,
            est_ttg_ms=est_ttg_ms,
            impacted_modules=impacted_modules,
            coverage_delta=coverage_delta,
            checks=checks
        )
    
    def _check_git_apply(self, diff: str) -> PreflightCheck:
        """Verifica se o diff pode ser aplicado"""
        start_time = self._get_time_ms()
        
        try:
            # Cria workspace temporário
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = pathlib.Path(temp_dir)
                
                # Cria ficheiros dummy para simular apply
                self._create_dummy_files(temp_path, diff)
                
                # Tenta aplicar o diff
                result = subprocess.run(
                    ["git", "apply", "--check"],
                    input=diff.encode(),
                    capture_output=True,
                    text=True,
                    cwd=temp_path,
                    timeout=self.check_timeout
                )
                
                passed = result.returncode == 0
                details = result.stdout if passed else result.stderr
                
        except Exception as e:
            passed = False
            details = f"Erro no git apply check: {e}"
        
        duration = self._get_time_ms() - start_time
        
        return PreflightCheck("git_apply_check", passed, details, duration)
    
    def _check_typecheck_incremental(self, changed_files: List[str]) -> PreflightCheck:
        """Verifica typecheck apenas nos ficheiros alterados"""
        start_time = self._get_time_ms()
        
        try:
            # Filtra ficheiros TypeScript/JavaScript
            ts_files = [f for f in changed_files if f.endswith(('.ts', '.tsx', '.js', '.jsx'))]
            
            if not ts_files:
                return PreflightCheck("typecheck_incremental", True, "Nenhum ficheiro TS/JS alterado", 0)
            
            # Simula typecheck (em produção, executaria tsc real)
            passed = True
            details = f"Typecheck em {len(ts_files)} ficheiros: {', '.join(ts_files)}"
            
            # Simula alguns erros de tipo
            for file in ts_files:
                if "error" in file.lower():
                    passed = False
                    details += f"\nErro de tipo em {file}"
            
        except Exception as e:
            passed = False
            details = f"Erro no typecheck: {e}"
        
        duration = self._get_time_ms() - start_time
        
        return PreflightCheck("typecheck_incremental", passed, details, duration)
    
    def _check_lint_incremental(self, changed_files: List[str]) -> PreflightCheck:
        """Verifica lint apenas nos ficheiros alterados"""
        start_time = self._get_time_ms()
        
        try:
            # Filtra ficheiros relevantes
            lint_files = [f for f in changed_files if f.endswith(('.ts', '.tsx', '.js', '.jsx', '.py'))]
            
            if not lint_files:
                return PreflightCheck("lint_incremental", True, "Nenhum ficheiro para lint", 0)
            
            # Simula lint (em produção, executaria eslint/ruff real)
            passed = True
            details = f"Lint em {len(lint_files)} ficheiros: {', '.join(lint_files)}"
            
            # Simula alguns problemas de lint
            for file in lint_files:
                if "lint" in file.lower():
                    passed = False
                    details += f"\nProblema de lint em {file}"
            
        except Exception as e:
            passed = False
            details = f"Erro no lint: {e}"
        
        duration = self._get_time_ms() - start_time
        
        return PreflightCheck("lint_incremental", passed, details, duration)
    
    def _check_test_selection(self, changed_files: List[str], graph: Dict[str, Any]) -> PreflightCheck:
        """Seleciona e verifica testes afetados"""
        start_time = self._get_time_ms()
        
        try:
            # Identifica testes relacionados aos ficheiros alterados
            affected_tests = self._identify_affected_tests(changed_files, graph)
            
            if not affected_tests:
                return PreflightCheck("test_selection", True, "Nenhum teste afetado", 0)
            
            # Simula execução dos testes selecionados
            passed = True
            details = f"Testes afetados: {len(affected_tests)} ({', '.join(affected_tests)})"
            
            # Simula falha em alguns testes
            for test in affected_tests:
                if "fail" in test.lower():
                    passed = False
                    details += f"\nTeste falhou: {test}"
            
        except Exception as e:
            passed = False
            details = f"Erro na seleção de testes: {e}"
        
        duration = self._get_time_ms() - start_time
        
        return PreflightCheck("test_selection", passed, details, duration)
    
    def _check_perf_sentinels(self, changed_files: List[str]) -> PreflightCheck:
        """Verifica sentinelas de performance"""
        start_time = self._get_time_ms()
        
        try:
            # Identifica funções críticas de performance
            critical_functions = self._identify_critical_functions(changed_files)
            
            if not critical_functions:
                return PreflightCheck("perf_sentinels", True, "Nenhuma função crítica afetada", 0)
            
            # Simula micro-benchmark das funções críticas
            passed = True
            details = f"Funções críticas afetadas: {len(critical_functions)}"
            
            # Simula degradação de performance
            for func in critical_functions:
                if "slow" in func.lower():
                    passed = False
                    details += f"\nDegradação de performance em {func}"
            
        except Exception as e:
            passed = False
            details = f"Erro nas sentinelas de performance: {e}"
        
        duration = self._get_time_ms() - start_time
        
        return PreflightCheck("perf_sentinels", passed, details, duration)
    
    def _check_secret_scan(self, diff: str) -> PreflightCheck:
        """Escaneia o diff por segredos"""
        start_time = self._get_time_ms()
        
        try:
            # Padrões de segredos
            secret_patterns = [
                r"api[_-]?key\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}['\"]",
                r"secret\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}['\"]",
                r"password\s*[:=]\s*['\"][A-Za-z0-9_\-]{8,}['\"]",
                r"token\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}['\"]"
            ]
            
            found_secrets = []
            for pattern in secret_patterns:
                matches = re.findall(pattern, diff, re.IGNORECASE)
                found_secrets.extend(matches)
            
            passed = len(found_secrets) == 0
            details = f"Segredos encontrados: {len(found_secrets)}"
            
            if found_secrets:
                details += f"\nSegredos: {found_secrets[:3]}"  # Mostra apenas os primeiros 3
            
        except Exception as e:
            passed = False
            details = f"Erro no scan de segredos: {e}"
        
        duration = self._get_time_ms() - start_time
        
        return PreflightCheck("secret_scan", passed, details, duration)
    
    def _create_dummy_files(self, temp_path: pathlib.Path, diff: str) -> None:
        """Cria ficheiros dummy para simular git apply"""
        # Extrai nomes de ficheiros do diff
        file_pattern = r"^\+\+\+ b/(.+)$"
        files = re.findall(file_pattern, diff, re.MULTILINE)
        
        for file_path in files:
            full_path = temp_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.touch()
    
    def _identify_affected_tests(self, changed_files: List[str], graph: Dict[str, Any]) -> List[str]:
        """Identifica testes afetados pelas mudanças"""
        affected_tests = []
        
        # Simplificado - procura por ficheiros de teste relacionados
        for file in changed_files:
            base_name = pathlib.Path(file).stem
            test_patterns = [
                f"{base_name}.test.ts",
                f"{base_name}.spec.ts",
                f"{base_name}.test.js",
                f"{base_name}.spec.js"
            ]
            
            for pattern in test_patterns:
                if pattern in str(changed_files):
                    affected_tests.append(pattern)
        
        return affected_tests
    
    def _identify_critical_functions(self, changed_files: List[str]) -> List[str]:
        """Identifica funções críticas de performance"""
        critical_functions = []
        
        # Simplificado - identifica funções comuns que podem ser críticas
        critical_patterns = [
            "sort", "filter", "map", "reduce",
            "render", "update", "process", "calculate"
        ]
        
        for file in changed_files:
            for pattern in critical_patterns:
                if pattern in file.lower():
                    critical_functions.append(f"{file}:{pattern}")
        
        return critical_functions
    
    def _identify_impacted_modules(self, changed_files: List[str], graph: Dict[str, Any]) -> List[str]:
        """Identifica módulos impactados pelas mudanças"""
        impacted = set()
        
        for file in changed_files:
            # Determina módulo baseado no caminho
            if "src/core/" in file:
                impacted.add("core")
            elif "src/components/" in file:
                impacted.add("components")
            elif "src/utils/" in file:
                impacted.add("utils")
            elif "src/infra/" in file:
                impacted.add("infrastructure")
            elif "tests/" in file:
                impacted.add("tests")
        
        return list(impacted)
    
    def _estimate_coverage_delta(self, changed_files: List[str], graph: Dict[str, Any]) -> float:
        """Estima mudança na cobertura de testes"""
        # Simplificado - estima baseado no número de ficheiros alterados
        total_files = len(graph.get("nodes", {}))
        changed_count = len(changed_files)
        
        if total_files == 0:
            return 0.0
        
        # Assume que cada ficheiro alterado pode afetar cobertura
        coverage_delta = (changed_count / total_files) * 0.1  # 10% por ficheiro
        
        return min(1.0, coverage_delta)
    
    def _estimate_ttg(self, checks: List[PreflightCheck]) -> int:
        """Estima TTG baseado nos checks"""
        total_duration = sum(check.duration_ms for check in checks)
        
        # Adiciona overhead estimado
        overhead = len(checks) * 50  # 50ms por check
        
        return total_duration + overhead
    
    def _get_time_ms(self) -> int:
        """Retorna tempo atual em milissegundos"""
        import time
        return int(time.time() * 1000)
    
    def generate_preflight_report(self, result: PreflightResult) -> str:
        """Gera relatório do preflight"""
        report = ["# Relatório Preflight Impact Simulator\n"]
        
        status = "✅ PASSOU" if result.preflight_ok else "❌ FALHOU"
        report.append(f"## Status: **{status}**")
        report.append(f"## TTG Estimado: **{result.est_ttg_ms}ms**")
        report.append(f"## Cobertura Delta: **{result.coverage_delta:.1%}**")
        report.append("")
        
        report.append("## Módulos Impactados")
        for module in result.impacted_modules:
            report.append(f"- {module}")
        report.append("")
        
        report.append("## Checks Executados")
        for check in result.checks:
            status = "✅" if check.passed else "❌"
            report.append(f"### {status} {check.name}")
            report.append(f"- **Duração**: {check.duration_ms}ms")
            report.append(f"- **Detalhes**: {check.details}")
            report.append("")
        
        if result.failing_checks:
            report.append("## Checks Falhados")
            for check_name in result.failing_checks:
                report.append(f"- {check_name}")
        
        return "\n".join(report)
