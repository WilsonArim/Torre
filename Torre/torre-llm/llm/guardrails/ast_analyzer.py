from __future__ import annotations
import ast
import re
from typing import Dict, Any, List, Set, Optional
from dataclasses import dataclass

@dataclass
class ImportInfo:
    """Informação sobre um import"""
    module: str
    alias: Optional[str]
    line: int
    is_relative: bool

@dataclass
class ASTAnalysis:
    """Análise AST de um ficheiro"""
    imports: List[ImportInfo]
    functions: List[str]
    classes: List[str]
    variables: List[str]
    complexity_score: float

class ASTAnalyzer:
    """
    Analisador AST para validação arquitetural rigorosa
    Objetivo: substituir checks simples por análise AST completa
    """
    
    def __init__(self):
        self.layer_patterns = {
            "ui": ["src/components/", "src/ui/", "src/pages/", "src/screens/"],
            "business": ["src/services/", "src/business/", "src/logic/"],
            "data": ["src/repositories/", "src/data/", "src/db/"],
            "infrastructure": ["src/infra/", "src/infrastructure/", "src/config/"]
        }
        
        self.forbidden_imports = {
            "ui": ["infrastructure", "data"],
            "business": ["infrastructure"],
            "data": ["ui"],
            "infrastructure": []  # Infra pode importar tudo
        }
    
    def analyze_file(self, content: str, file_path: str) -> ASTAnalysis:
        """Analisa um ficheiro usando AST"""
        try:
            tree = ast.parse(content)
            return self._analyze_ast_tree(tree, file_path)
        except SyntaxError:
            # Fallback para análise regex se AST falhar
            return self._fallback_analysis(content, file_path)
    
    def _analyze_ast_tree(self, tree: ast.AST, file_path: str) -> ASTAnalysis:
        """Analisa árvore AST"""
        imports = []
        functions = []
        classes = []
        variables = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(ImportInfo(
                        module=alias.name,
                        alias=alias.asname,
                        line=node.lineno,
                        is_relative=False
                    ))
            elif isinstance(node, ast.ImportFrom):
                imports.append(ImportInfo(
                    module=node.module or "",
                    alias=node.names[0].asname if node.names else None,
                    line=node.lineno,
                    is_relative=node.level > 0
                ))
            elif isinstance(node, ast.FunctionDef):
                functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        variables.append(target.id)
        
        # Calcula complexidade ciclomática
        complexity = self._calculate_complexity(tree)
        
        return ASTAnalysis(
            imports=imports,
            functions=functions,
            classes=classes,
            variables=variables,
            complexity_score=complexity
        )
    
    def _calculate_complexity(self, tree: ast.AST) -> float:
        """Calcula complexidade ciclomática"""
        complexity = 1.0  # Base
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, ast.With):
                complexity += 1
            elif isinstance(node, ast.Try):
                complexity += 1
        
        return complexity
    
    def _fallback_analysis(self, content: str, file_path: str) -> ASTAnalysis:
        """Análise fallback usando regex"""
        imports = []
        functions = []
        classes = []
        variables = []
        
        lines = content.split('\n')
        
        # Regex patterns
        import_pattern = r'^(\s*)(?:from\s+([^\s]+)\s+import|import\s+([^\s]+))'
        function_pattern = r'^\s*(?:def|function)\s+(\w+)'
        class_pattern = r'^\s*class\s+(\w+)'
        var_pattern = r'^\s*(?:const|let|var)\s+(\w+)'
        
        for i, line in enumerate(lines, 1):
            # Imports
            import_match = re.match(import_pattern, line)
            if import_match:
                module = import_match.group(2) or import_match.group(3)
                imports.append(ImportInfo(
                    module=module,
                    alias=None,
                    line=i,
                    is_relative=module.startswith('.')
                ))
            
            # Functions
            func_match = re.match(function_pattern, line)
            if func_match:
                functions.append(func_match.group(1))
            
            # Classes
            class_match = re.match(class_pattern, line)
            if class_match:
                classes.append(class_match.group(1))
            
            # Variables
            var_match = re.match(var_pattern, line)
            if var_match:
                variables.append(var_match.group(1))
        
        return ASTAnalysis(
            imports=imports,
            functions=functions,
            classes=classes,
            variables=variables,
            complexity_score=1.0  # Simplificado
        )
    
    def validate_architecture(self, analysis: ASTAnalysis, file_path: str) -> List[Dict[str, Any]]:
        """Valida arquitetura baseado em análise AST"""
        violations = []
        
        # Determina camada do ficheiro
        file_layer = self._determine_layer(file_path)
        
        # Valida imports
        for import_info in analysis.imports:
            import_layer = self._determine_import_layer(import_info.module, file_path)
            
            if self._is_forbidden_import(file_layer, import_layer):
                violations.append({
                    "kind": "arch/layer_violation",
                    "severity": "block",
                    "path": file_path,
                    "line": import_info.line,
                    "msg": f"Import proibido: {file_layer} → {import_layer} ({import_info.module})"
                })
        
        # Valida complexidade
        if analysis.complexity_score > 10:
            violations.append({
                "kind": "arch/complexity",
                "severity": "advisory",
                "path": file_path,
                "line": 0,
                "msg": f"Complexidade ciclomática alta: {analysis.complexity_score:.1f}"
            })
        
        return violations
    
    def _determine_layer(self, file_path: str) -> str:
        """Determina camada arquitetural do ficheiro"""
        file_path_lower = file_path.lower()
        
        for layer, patterns in self.layer_patterns.items():
            for pattern in patterns:
                if pattern in file_path_lower:
                    return layer
        
        return "unknown"
    
    def _determine_import_layer(self, import_module: str, current_file: str) -> str:
        """Determina camada de um import"""
        # Para imports relativos, analisa o caminho
        if import_module.startswith('.'):
            # Simplificado - assume que é relativo ao ficheiro atual
            return self._determine_layer(current_file)
        
        # Para imports absolutos, tenta inferir
        module_lower = import_module.lower()
        
        if any(pattern in module_lower for pattern in ["ui", "component", "page"]):
            return "ui"
        elif any(pattern in module_lower for pattern in ["service", "business", "logic"]):
            return "business"
        elif any(pattern in module_lower for pattern in ["repo", "data", "db", "model"]):
            return "data"
        elif any(pattern in module_lower for pattern in ["infra", "config", "util"]):
            return "infrastructure"
        
        return "unknown"
    
    def _is_forbidden_import(self, from_layer: str, to_layer: str) -> bool:
        """Verifica se um import é proibido"""
        if from_layer not in self.forbidden_imports:
            return False
        
        return to_layer in self.forbidden_imports[from_layer]
    
    def analyze_import_graph(self, files_analysis: Dict[str, ASTAnalysis]) -> Dict[str, Any]:
        """Analisa grafo de imports completo"""
        graph = {
            "nodes": {},
            "edges": [],
            "violations": [],
            "metrics": {
                "total_files": len(files_analysis),
                "total_imports": 0,
                "layer_violations": 0,
                "circular_deps": 0
            }
        }
        
        # Constrói grafo
        for file_path, analysis in files_analysis.items():
            layer = self._determine_layer(file_path)
            graph["nodes"][file_path] = {
                "layer": layer,
                "imports": len(analysis.imports),
                "functions": len(analysis.functions),
                "complexity": analysis.complexity_score
            }
            
            graph["metrics"]["total_imports"] += len(analysis.imports)
            
            # Adiciona edges e detecta violações
            for import_info in analysis.imports:
                import_layer = self._determine_import_layer(import_info.module, file_path)
                
                graph["edges"].append({
                    "from": file_path,
                    "to": import_info.module,
                    "from_layer": layer,
                    "to_layer": import_layer
                })
                
                if self._is_forbidden_import(layer, import_layer):
                    graph["violations"].append({
                        "file": file_path,
                        "import": import_info.module,
                        "from_layer": layer,
                        "to_layer": import_layer,
                        "line": import_info.line
                    })
                    graph["metrics"]["layer_violations"] += 1
        
        # Detecta dependências circulares
        graph["metrics"]["circular_deps"] = self._detect_circular_dependencies(graph)
        
        return graph
    
    def _detect_circular_dependencies(self, graph: Dict[str, Any]) -> int:
        """Detecta dependências circulares no grafo"""
        # Implementação simplificada
        # Em produção, usar algoritmo de detecção de ciclos
        return 0  # Placeholder
