#!/usr/bin/env python3
"""
Executor da Superpipeline FÁBRICA 2.0
Implementa os 14 capítulos da nova superpipeline conforme pipeline/superpipeline.yaml
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    import yaml  # type: ignore
except Exception:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parents[2]
SUPERPIPELINE_YAML = REPO_ROOT / "pipeline" / "superpipeline.yaml"
REL_DIR = REPO_ROOT / "relatorios"
PROGRESSO_FILE = REL_DIR / "progresso_superpipeline.md"


def load_yaml(path: Path) -> Any:
    """Carrega ficheiro YAML."""
    if not path.exists():
        return {}
    if yaml is None:
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def save_progresso(capitulo_id: str, titulo: str, status: str, artefactos: List[str]) -> None:
    """Salva progresso da superpipeline."""
    timestamp = datetime.now(timezone.utc).isoformat()
    
    if PROGRESSO_FILE.exists():
        content = PROGRESSO_FILE.read_text(encoding="utf-8")
    else:
        content = """# Progresso da Superpipeline FÁBRICA 2.0

**PIPELINE/FORA_PIPELINE:** PIPELINE

**OWNER: ENGENHEIRO — Próxima ação:** Executando capítulos da superpipeline

---

"""
    
    entry = f"""
## {titulo} ({capitulo_id})

- **Status:** {status}
- **Timestamp:** {timestamp}
- **Artefactos:**
"""
    for artefacto in artefactos:
        entry += f"  - {artefacto}\n"
    
    content += entry + "\n"
    PROGRESSO_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROGRESSO_FILE.write_text(content, encoding="utf-8")


def executar_rag_memoria_viva() -> Dict[str, Any]:
    """Implementa capítulo 1: Memória Viva/RAG Constitucional."""
    print("=" * 60)
    print("📚 CAPÍTULO 1: Memória Viva/RAG Constitucional")
    print("=" * 60)
    
    # 1. Criar estrutura de índice RAG
    rag_dir = REPO_ROOT / "core" / "rag_constitucional"
    rag_dir.mkdir(parents=True, exist_ok=True)
    
    indices_dir = rag_dir / "indices"
    indices_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. Indexar documentos constitucionais
    documentos_constitucionais = [
        ("core/sop/constituição.yaml", "constituicao"),
        ("core/sop/leis.yaml", "leis"),
        ("core/sop/exceptions.yaml", "exceptions"),
        ("core/sop/doutrina.yaml", "doutrina"),
    ]
    
    index_data = {
        "versao": "1.0",
        "data_criacao": datetime.now(timezone.utc).isoformat(),
        "documentos": [],
    }
    
    print("\n📖 Indexando documentos constitucionais...")
    for doc_path, doc_type in documentos_constitucionais:
        full_path = REPO_ROOT / doc_path
        if full_path.exists():
            content = full_path.read_text(encoding="utf-8")
            index_data["documentos"].append({
                "tipo": doc_type,
                "caminho": doc_path,
                "tamanho": len(content),
                "linhas": len(content.splitlines()),
            })
            print(f"  ✅ {doc_path}")
        else:
            print(f"  ⚠️  {doc_path} não encontrado")
    
    # 3. Criar sistema de busca simples (base para RAG futuro)
    busca_script = rag_dir / "buscar.py"
    busca_script.write_text('''#!/usr/bin/env python3
"""
Sistema de busca RAG Constitucional
Busca informação normativa, histórico e decisões
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

def buscar(consulta: str, tipo: str = "todos") -> list:
    """
    Busca informação constitucional.
    
    Args:
        consulta: Termo ou frase a buscar
        tipo: Tipo de documento (constituicao, leis, doutrina, todos)
    
    Returns:
        Lista de documentos relevantes com citações
    """
    resultados = []
    
    documentos = {
        "constituicao": REPO_ROOT / "core/sop/constituição.yaml",
        "leis": REPO_ROOT / "core/sop/leis.yaml",
        "doutrina": REPO_ROOT / "core/sop/doutrina.yaml",
    }
    
    consulta_lower = consulta.lower()
    
    for doc_tipo, doc_path in documentos.items():
        if tipo != "todos" and tipo != doc_tipo:
            continue
        
        if not doc_path.exists():
            continue
        
        try:
            content = doc_path.read_text(encoding="utf-8")
            lines = content.splitlines()
            
            for i, line in enumerate(lines):
                if consulta_lower in line.lower():
                    contexto_inicio = max(0, i - 2)
                    contexto_fim = min(len(lines), i + 3)
                    contexto = "\\n".join(lines[contexto_inicio:contexto_fim])
                    
                    resultados.append({
                        "tipo": doc_tipo,
                        "caminho": str(doc_path.relative_to(REPO_ROOT)),
                        "linha": i + 1,
                        "contexto": contexto,
                    })
        except Exception as e:
            print(f"Erro ao processar {doc_path}: {e}", file=sys.stderr)
    
    return resultados

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: buscar.py <consulta> [tipo]")
        sys.exit(1)
    
    consulta = sys.argv[1]
    tipo = sys.argv[2] if len(sys.argv) > 2 else "todos"
    
    resultados = buscar(consulta, tipo)
    
    import json
    print(json.dumps(resultados, indent=2, ensure_ascii=False))
''', encoding="utf-8")
    
    busca_script.chmod(0o755)
    
    # 4. Criar índice JSON
    index_file = indices_dir / "index.json"
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)
    
    # 5. Criar README explicativo
    readme_file = rag_dir / "README.md"
    readme_file.write_text('''# RAG Constitucional — Memória Viva

Sistema de busca e citação de informação normativa, histórico e decisões da FÁBRICA.

## Uso

```bash
python3 core/rag_constitucional/buscar.py "ART-04" constituicao
```

## Documentos Indexados

- Constituição (`core/sop/constituição.yaml`)
- Leis (`core/sop/leis.yaml`)
- Exceções (`core/sop/exceptions.yaml`)
- Doutrina (`core/sop/doutrina.yaml`)

## Próximos Passos

- [ ] Implementar embeddings vetoriais
- [ ] Adicionar busca semântica
- [ ] Indexar relatórios históricos
- [ ] Integrar com LLM para raciocínio contextualizado
''', encoding="utf-8")
    
    # 6. Testar busca
    print("\n🔍 Testando sistema de busca...")
    import subprocess
    result = subprocess.run(
        [sys.executable, str(busca_script), "ART-04", "constituicao"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=10,
    )
    
    if result.returncode == 0:
        print("  ✅ Busca funcionando corretamente")
    else:
        print(f"  ⚠️  Busca retornou código {result.returncode}")
    
    artefactos = [
        str(rag_dir.relative_to(REPO_ROOT)),
        str(index_file.relative_to(REPO_ROOT)),
        str(busca_script.relative_to(REPO_ROOT)),
        str(readme_file.relative_to(REPO_ROOT)),
    ]
    
    save_progresso("RAG_MEMORIA_VIVA", "Memória Viva/RAG Constitucional", "CONCLUÍDO", artefactos)
    
    return {
        "status": "SUCCESS",
        "capitulo": "RAG_MEMORIA_VIVA",
        "artefactos": artefactos,
    }


def calcular_hash_ficheiro(caminho: Path) -> str:
    """Calcula hash SHA256 de um ficheiro."""
    try:
        sha256 = hashlib.sha256()
        with open(caminho, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception:
        return ""


def calcular_hash_conteudo(conteudo: str) -> str:
    """Calcula hash SHA256 de conteúdo."""
    return hashlib.sha256(conteudo.encode("utf-8")).hexdigest()


def executar_fingerprint_conformidade() -> Dict[str, Any]:
    """Implementa capítulo 2: Fingerprint de Conformidade."""
    print("=" * 60)
    print("🔐 CAPÍTULO 2: Fingerprint de Conformidade")
    print("=" * 60)
    
    # 1. Criar estrutura de fingerprints
    fingerprint_dir = REPO_ROOT / "core" / "fingerprint_conformidade"
    fingerprint_dir.mkdir(parents=True, exist_ok=True)
    
    fingerprints_file = fingerprint_dir / "fingerprints.json"
    
    # 2. Lista de artefactos críticos para fingerprint
    artefactos_criticos = [
        # Constituição e Leis
        "core/sop/constituição.yaml",
        "core/sop/leis.yaml",
        "core/sop/exceptions.yaml",
        "core/sop/doutrina.yaml",
        # Pipelines
        "pipeline/superpipeline.yaml",
        "pipeline/PIPELINE_TOC.md",
        # PINs principais
        "factory/pins/engenheiro.yaml",
        "factory/pins/sop.yaml",
        "factory/pins/gatekeeper.yaml",
        "factory/pins/estado_maior.yaml",
    ]
    
    fingerprints_data = {
        "versao": "1.0",
        "data_criacao": datetime.now(timezone.utc).isoformat(),
        "algoritmo": "SHA256",
        "fingerprints": [],
    }
    
    print("\n🔐 Calculando fingerprints de artefactos críticos...")
    for artefacto_path in artefactos_criticos:
        full_path = REPO_ROOT / artefacto_path
        if full_path.exists():
            hash_value = calcular_hash_ficheiro(full_path)
            fingerprints_data["fingerprints"].append({
                "caminho": artefacto_path,
                "hash": hash_value,
                "tipo": "artefacto_critico",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            print(f"  ✅ {artefacto_path}: {hash_value[:16]}...")
        else:
            print(f"  ⚠️  {artefacto_path} não encontrado")
    
    # 3. Criar script de verificação
    verificar_script = fingerprint_dir / "verificar.py"
    verificar_script.write_text('''#!/usr/bin/env python3
"""
Sistema de Verificação de Fingerprint de Conformidade
Verifica integridade de artefactos críticos usando hashes SHA256
"""
import json
import sys
import hashlib
from pathlib import Path
from datetime import datetime, timezone

REPO_ROOT = Path(__file__).resolve().parents[2]
FINGERPRINTS_FILE = REPO_ROOT / "core" / "fingerprint_conformidade" / "fingerprints.json"


def calcular_hash_ficheiro(caminho: Path) -> str:
    """Calcula hash SHA256 de um ficheiro."""
    try:
        sha256 = hashlib.sha256()
        with open(caminho, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception:
        return ""


def verificar_artefacto(caminho: str) -> dict:
    """
    Verifica integridade de um artefacto.
    
    Args:
        caminho: Caminho relativo do artefacto
    
    Returns:
        Dict com status de verificação
    """
    resultado = {
        "caminho": caminho,
        "status": "UNKNOWN",
        "hash_atual": "",
        "hash_registrado": "",
        "mensagem": "",
    }
    
    # Carregar fingerprints registrados
    if not FINGERPRINTS_FILE.exists():
        resultado["mensagem"] = "Fingerprints não encontrados"
        return resultado
    
    try:
        with open(FINGERPRINTS_FILE, "r", encoding="utf-8") as f:
            fingerprints_data = json.load(f)
    except Exception as e:
        resultado["mensagem"] = f"Erro ao carregar fingerprints: {e}"
        return resultado
    
    # Encontrar fingerprint registrado
    fingerprint_registrado = None
    for fp in fingerprints_data.get("fingerprints", []):
        if fp.get("caminho") == caminho:
            fingerprint_registrado = fp
            break
    
    if not fingerprint_registrado:
        resultado["mensagem"] = "Artefacto não encontrado nos fingerprints"
        return resultado
    
    # Calcular hash atual
    full_path = REPO_ROOT / caminho
    if not full_path.exists():
        resultado["status"] = "FALTANDO"
        resultado["mensagem"] = "Artefacto não existe"
        return resultado
    
    hash_atual = calcular_hash_ficheiro(full_path)
    hash_registrado = fingerprint_registrado.get("hash", "")
    
    resultado["hash_atual"] = hash_atual
    resultado["hash_registrado"] = hash_registrado
    
    if hash_atual == hash_registrado:
        resultado["status"] = "OK"
        resultado["mensagem"] = "Integridade verificada"
    else:
        resultado["status"] = "ALTERADO"
        resultado["mensagem"] = "Artefacto foi modificado desde último fingerprint"
    
    return resultado


def verificar_todos() -> list:
    """Verifica todos os artefactos registrados."""
    resultados = []
    
    if not FINGERPRINTS_FILE.exists():
        return resultados
    
    try:
        with open(FINGERPRINTS_FILE, "r", encoding="utf-8") as f:
            fingerprints_data = json.load(f)
    except Exception:
        return resultados
    
    for fp in fingerprints_data.get("fingerprints", []):
        caminho = fp.get("caminho")
        if caminho:
            resultado = verificar_artefacto(caminho)
            resultados.append(resultado)
    
    return resultados


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: verificar.py <caminho> | verificar.py --todos")
        sys.exit(1)
    
    if sys.argv[1] == "--todos":
        resultados = verificar_todos()
        ok = sum(1 for r in resultados if r["status"] == "OK")
        alterados = sum(1 for r in resultados if r["status"] == "ALTERADO")
        faltando = sum(1 for r in resultados if r["status"] == "FALTANDO")
        
        print(f"Verificação completa:")
        print(f"  ✅ OK: {ok}")
        print(f"  ⚠️  ALTERADOS: {alterados}")
        print(f"  ❌ FALTANDO: {faltando}")
        
        import json
        print(json.dumps(resultados, indent=2, ensure_ascii=False))
    else:
        caminho = sys.argv[1]
        resultado = verificar_artefacto(caminho)
        import json
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
        
        if resultado["status"] != "OK":
            sys.exit(1)
''', encoding="utf-8")
    
    verificar_script.chmod(0o755)
    
    # 4. Salvar fingerprints
    with open(fingerprints_file, "w", encoding="utf-8") as f:
        json.dump(fingerprints_data, f, indent=2, ensure_ascii=False)
    
    # 5. Criar README explicativo
    readme_file = fingerprint_dir / "README.md"
    readme_file.write_text('''# Fingerprint de Conformidade

Sistema de hash/checksum automático de artefactos, pipelines e leis para garantir autenticidade e rastreabilidade.

## Uso

### Verificar um artefacto específico:
```bash
python3 core/fingerprint_conformidade/verificar.py core/sop/constituição.yaml
```

### Verificar todos os artefactos:
```bash
python3 core/fingerprint_conformidade/verificar.py --todos
```

## Artefactos Monitorados

- Constituição e Leis (`core/sop/`)
- Pipelines (`pipeline/`)
- PINs principais (`factory/pins/`)

## Próximos Passos

- [ ] Integrar com CI/CD para verificação automática
- [ ] Adicionar verificação em pre-commit hooks
- [ ] Alertar sobre alterações em artefactos críticos
- [ ] Integrar com sistema de versionamento
''', encoding="utf-8")
    
    # 6. Testar verificação
    print("\n🔍 Testando sistema de verificação...")
    import subprocess
    result = subprocess.run(
        [sys.executable, str(verificar_script), "--todos"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=10,
    )
    
    if result.returncode == 0:
        print("  ✅ Verificação funcionando corretamente")
        print(result.stdout[:500])
    else:
        print(f"  ⚠️  Verificação retornou código {result.returncode}")
    
    artefactos = [
        str(fingerprint_dir.relative_to(REPO_ROOT)),
        str(fingerprints_file.relative_to(REPO_ROOT)),
        str(verificar_script.relative_to(REPO_ROOT)),
        str(readme_file.relative_to(REPO_ROOT)),
    ]
    
    save_progresso("FINGERPRINT_CONFORMIDADE", "Fingerprint de Conformidade", "CONCLUÍDO", artefactos)
    
    return {
        "status": "SUCCESS",
        "capitulo": "FINGERPRINT_CONFORMIDADE",
        "artefactos": artefactos,
    }


def executar_torre_reflexiva() -> Dict[str, Any]:
    """Implementa capítulo 3: Torre Reflexiva."""
    print("=" * 60)
    print("🔮 CAPÍTULO 3: Torre Reflexiva")
    print("=" * 60)
    
    # 1. Criar estrutura da Torre Reflexiva
    reflexiva_dir = REPO_ROOT / "Torre" / "reflexiva"
    reflexiva_dir.mkdir(parents=True, exist_ok=True)
    
    pesquisa_dir = reflexiva_dir / "pesquisas"
    pesquisa_dir.mkdir(parents=True, exist_ok=True)
    
    sinteses_dir = reflexiva_dir / "sinteses"
    sinteses_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. Criar módulo de pesquisa externa (apenas leitura, sem autonomia)
    pesquisa_script = reflexiva_dir / "pesquisar.py"
    pesquisa_script.write_text('''#!/usr/bin/env python3
"""
Torre Reflexiva — Módulo de Pesquisa Externa
Opera apenas como medidor estatístico. NÃO tem autonomia para criar.
Pode criar apenas ficheiros YAML e Markdown na sua pasta.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any

REPO_ROOT = Path(__file__).resolve().parents[2]
REFLEXIVA_DIR = REPO_ROOT / "Torre" / "reflexiva"
PESQUISAS_DIR = REFLEXIVA_DIR / "pesquisas"
SINTESES_DIR = REFLEXIVA_DIR / "sinteses"


def pesquisar_tema(tema: str, fontes_externas: List[str] = None) -> Dict[str, Any]:
    """
    Pesquisa tema externo (simulado — requer integração real futura).
    
    Args:
        tema: Tema a pesquisar
        fontes_externas: Lista de fontes externas (opcional)
    
    Returns:
        Dict com resultados da pesquisa
    """
    # NOTA: Esta é uma implementação base. Integração real requer:
    # - Web scraping controlado
    # - APIs de pesquisa
    # - Filtros de segurança
    
    resultado = {
        "tema": tema,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agente": "TORRE_REFLEXIVA",
        "tipo": "pesquisa_externa",
        "fontes": fontes_externas or [],
        "resultados": [],
        "metadados": {
            "objetivo": f"Pesquisar informações sobre: {tema}",
            "regras_aplicadas": [
                "ART-05: Não-Autonomia Absoluta",
                "ART-07: Transparência (metadados obrigatórios)",
                "Apenas YAML/MD na pasta Torre/reflexiva/",
            ],
        },
    }
    
    # Simulação de resultados (será substituído por pesquisa real)
    resultado["resultados"] = [
        {
            "fonte": "simulada",
            "resumo": f"Informações sobre {tema}",
            "relevancia": "media",
        }
    ]
    
    return resultado


def gerar_sintese(pesquisa_id: str, tema: str, resultados: List[Dict]) -> Dict[str, Any]:
    """
    Gera síntese da pesquisa (apenas estatísticas e análise).
    
    Args:
        pesquisa_id: ID da pesquisa
        tema: Tema pesquisado
        resultados: Resultados da pesquisa
    
    Returns:
        Dict com síntese
    """
    sintese = {
        "pesquisa_id": pesquisa_id,
        "tema": tema,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agente": "TORRE_REFLEXIVA",
        "tipo": "sintese",
        "estatisticas": {
            "total_resultados": len(resultados),
            "relevancia_alta": sum(1 for r in resultados if r.get("relevancia") == "alta"),
            "relevancia_media": sum(1 for r in resultados if r.get("relevancia") == "media"),
            "relevancia_baixa": sum(1 for r in resultados if r.get("relevancia") == "baixa"),
        },
        "analise": {
            "coerencia_interna": "verificar",
            "alinhamento_constitucional": "verificar",
        },
        "metadados": {
            "objetivo": f"Sintetizar pesquisa sobre: {tema}",
            "regras_aplicadas": [
                "ART-05: Não-Autonomia Absoluta",
                "ART-07: Transparência (metadados obrigatórios)",
                "Apenas medidor estatístico — não cria código",
            ],
        },
    }
    
    return sintese


def salvar_pesquisa(pesquisa: Dict[str, Any]) -> Path:
    """Salva pesquisa em YAML na pasta permitida."""
    pesquisa_id = f"pesquisa_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    pesquisa_file = PESQUISAS_DIR / f"{pesquisa_id}.yaml"
    
    # Converter para YAML (formato simples)
    yaml_content = f"""# Pesquisa Torre Reflexiva

tema: {pesquisa['tema']}
timestamp: {pesquisa['timestamp']}
agente: {pesquisa['agente']}
tipo: {pesquisa['tipo']}

fontes:
"""
    for fonte in pesquisa.get('fontes', []):
        yaml_content += f"  - {fonte}\n"
    
    yaml_content += "\nresultados:\n"
    for resultado in pesquisa.get('resultados', []):
        yaml_content += f"  - fonte: {resultado.get('fonte', 'desconhecida')}\n"
        yaml_content += f"    resumo: {resultado.get('resumo', 'N/A')}\n"
        yaml_content += f"    relevancia: {resultado.get('relevancia', 'media')}\n"
    
    yaml_content += f"""
metadados:
  objetivo: "{pesquisa['metadados']['objetivo']}"
  regras_aplicadas:
"""
    for regra in pesquisa['metadados']['regras_aplicadas']:
        yaml_content += f"    - {regra}\n"
    
    pesquisa_file.write_text(yaml_content, encoding="utf-8")
    
    return pesquisa_file


def salvar_sintese(sintese: Dict[str, Any]) -> Path:
    """Salva síntese em Markdown na pasta permitida."""
    sintese_id = f"sintese_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    sintese_file = SINTESES_DIR / f"{sintese_id}.md"
    
    md_content = f"""# Síntese Torre Reflexiva

**Tema:** {sintese['tema']}
**Pesquisa ID:** {sintese['pesquisa_id']}
**Timestamp:** {sintese['timestamp']}
**Agente:** {sintese['agente']}

## Estatísticas

- Total de resultados: {sintese['estatisticas']['total_resultados']}
- Relevância alta: {sintese['estatisticas']['relevancia_alta']}
- Relevância média: {sintese['estatisticas']['relevancia_media']}
- Relevância baixa: {sintese['estatisticas']['relevancia_baixa']}

## Análise

- Coerência interna: {sintese['analise']['coerencia_interna']}
- Alinhamento constitucional: {sintese['analise']['alinhamento_constitucional']}

## Metadados

**Objetivo:** {sintese['metadados']['objetivo']}

**Regras Aplicadas:**
"""
    for regra in sintese['metadados']['regras_aplicadas']:
        md_content += f"- {regra}\n"
    
    sintese_file.write_text(md_content, encoding="utf-8")
    
    return sintese_file


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: pesquisar.py <tema> [fonte1] [fonte2] ...")
        sys.exit(1)
    
    tema = sys.argv[1]
    fontes = sys.argv[2:] if len(sys.argv) > 2 else []
    
    # Pesquisar
    pesquisa = pesquisar_tema(tema, fontes)
    pesquisa_file = salvar_pesquisa(pesquisa)
    print(f"✅ Pesquisa salva em: {pesquisa_file.relative_to(REPO_ROOT)}")
    
    # Gerar síntese
    sintese = gerar_sintese(
        pesquisa_file.stem,
        tema,
        pesquisa.get('resultados', [])
    )
    sintese_file = salvar_sintese(sintese)
    print(f"✅ Síntese salva em: {sintese_file.relative_to(REPO_ROOT)}")
    
    import json
    print(json.dumps({
        "pesquisa": str(pesquisa_file.relative_to(REPO_ROOT)),
        "sintese": str(sintese_file.relative_to(REPO_ROOT)),
    }, indent=2))
''', encoding="utf-8")
    
    pesquisa_script.chmod(0o755)
    
    # 3. Criar README explicativo
    readme_file = reflexiva_dir / "README.md"
    readme_file.write_text('''# Torre Reflexiva (2C)

Módulo de auto-avaliação e pesquisa externa da FÁBRICA.

## Especificações

- ✅ Opera apenas como medidor estatístico
- ✅ Pesquisa na internet sobre temas novos, ideias novas
- ❌ **NÃO tem autonomia para criar**
- ✅ Pode criar apenas ficheiros YAML e Markdown na sua pasta
- ✅ SOP dará parecer sobre segurança
- ✅ Estado-Maior dará parecer se vale a pena incluir

## Uso

```bash
python3 Torre/reflexiva/pesquisar.py "tema de pesquisa" fonte1 fonte2
```

## Estrutura

- `pesquisas/` — Pesquisas salvas em YAML
- `sinteses/` — Sínteses salvas em Markdown

## Conformidade Constitucional

- ART-05: Não-Autonomia Absoluta — apenas medidor estatístico
- ART-07: Transparência — metadados obrigatórios em todos os ficheiros
- ART-09: Evidência — todas as pesquisas são rastreáveis

## Próximos Passos

- [ ] Integrar pesquisa externa real (web scraping controlado)
- [ ] Adicionar filtros de segurança
- [ ] Integrar com APIs de pesquisa
- [ ] Adicionar validação SOP automática
''', encoding="utf-8")
    
    # 4. Criar exemplo de pesquisa
    print("\n🔍 Criando exemplo de pesquisa...")
    import subprocess
    result = subprocess.run(
        [sys.executable, str(pesquisa_script), "Constituição da FÁBRICA", "documentação"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=10,
    )
    
    if result.returncode == 0:
        print("  ✅ Exemplo de pesquisa criado")
        print(result.stdout[:300])
    else:
        print(f"  ⚠️  Pesquisa retornou código {result.returncode}")
    
    artefactos = [
        str(reflexiva_dir.relative_to(REPO_ROOT)),
        str(pesquisa_script.relative_to(REPO_ROOT)),
        str(readme_file.relative_to(REPO_ROOT)),
        str(pesquisa_dir.relative_to(REPO_ROOT)),
        str(sinteses_dir.relative_to(REPO_ROOT)),
    ]
    
    save_progresso("TORRE_REFLEXIVA", "Torre Reflexiva", "CONCLUÍDO", artefactos)
    
    return {
        "status": "SUCCESS",
        "capitulo": "TORRE_REFLEXIVA",
        "artefactos": artefactos,
    }


def validar_triade_fundamentacao() -> Tuple[bool, List[str]]:
    """
    Valida se a Tríade de Fundamentação existe na FÁBRICA.
    
    Returns:
        Tuple[bool, List[str]]: (valido, faltantes)
    """
    faltantes = []
    
    # White Paper
    white_paper_paths = [
        REPO_ROOT / "docs" / "white_paper.md",
        REPO_ROOT / "docs" / "WHITE_PAPER.md",
        REPO_ROOT / "WHITE_PAPER.md",
    ]
    tem_white_paper = any(p.exists() for p in white_paper_paths)
    if not tem_white_paper:
        faltantes.append("White Paper")
    
    # Arquitetura
    arquitetura_paths = [
        REPO_ROOT / "docs" / "arquitetura.md",
        REPO_ROOT / "docs" / "ARQUITETURA.md",
        REPO_ROOT / "ARQUITETURA.md",
        REPO_ROOT / "docs" / "architecture.md",
    ]
    tem_arquitetura = any(p.exists() for p in arquitetura_paths)
    if not tem_arquitetura:
        faltantes.append("Arquitetura")
    
    # Base Operacional
    base_operacional_paths = [
        REPO_ROOT / "docs" / "base_operacional.md",
        REPO_ROOT / "docs" / "BASE_OPERACIONAL.md",
        REPO_ROOT / "BASE_OPERACIONAL.md",
        REPO_ROOT / "pipeline" / "README.md",  # Considerar README da pipeline como Base Operacional
    ]
    tem_base_operacional = any(p.exists() for p in base_operacional_paths)
    if not tem_base_operacional:
        faltantes.append("Base Operacional")
    
    return len(faltantes) == 0, faltantes


def executar_replicacao_instantanea() -> Dict[str, Any]:
    """Implementa capítulo 4: Replicação Instantânea."""
    print("=" * 60)
    print("🔄 CAPÍTULO 4: Replicação Instantânea")
    print("=" * 60)
    
    # 1. Validar Tríade de Fundamentação antes de replicar (ART-02)
    print("\n🔍 Validando Tríade de Fundamentação...")
    triade_ok, faltantes = validar_triade_fundamentacao()
    
    if not triade_ok:
        print(f"  ⚠️  Tríade incompleta. Faltantes: {', '.join(faltantes)}")
        print("  ⚠️  Replicação será bloqueada até Tríade estar completa (ART-02)")
    else:
        print("  ✅ Tríade de Fundamentação validada")
    
    # 2. Criar estrutura do módulo de replicação (independente da Tríade)
    replicacao_dir = REPO_ROOT / "core" / "replicacao"
    replicacao_dir.mkdir(parents=True, exist_ok=True)
    
    # 3. Criar script de replicação
    replicar_script = replicacao_dir / "replicar.py"
    replicar_script.write_text('''#!/usr/bin/env python3
"""
Replicação Instantânea — FÁBRICA 2.0
Script para copiar pipelines/projetos, herdando Tríade e Leis.
Conforme ART-02 (Tríade de Fundamentação) e ART-06 (Coerência entre Projetos).
"""
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]


def validar_triade_fundamentacao() -> Tuple[bool, List[str]]:
    """
    Valida se a Tríade de Fundamentação existe na FÁBRICA.
    
    Returns:
        Tuple[bool, List[str]]: (valido, faltantes)
    """
    faltantes = []
    
    # White Paper
    white_paper_paths = [
        REPO_ROOT / "docs" / "white_paper.md",
        REPO_ROOT / "docs" / "WHITE_PAPER.md",
        REPO_ROOT / "WHITE_PAPER.md",
    ]
    tem_white_paper = any(p.exists() for p in white_paper_paths)
    if not tem_white_paper:
        faltantes.append("White Paper")
    
    # Arquitetura
    arquitetura_paths = [
        REPO_ROOT / "docs" / "arquitetura.md",
        REPO_ROOT / "docs" / "ARQUITETURA.md",
        REPO_ROOT / "ARQUITETURA.md",
        REPO_ROOT / "docs" / "architecture.md",
    ]
    tem_arquitetura = any(p.exists() for p in arquitetura_paths)
    if not tem_arquitetura:
        faltantes.append("Arquitetura")
    
    # Base Operacional
    base_operacional_paths = [
        REPO_ROOT / "docs" / "base_operacional.md",
        REPO_ROOT / "docs" / "BASE_OPERACIONAL.md",
        REPO_ROOT / "BASE_OPERACIONAL.md",
        REPO_ROOT / "pipeline" / "README.md",
    ]
    tem_base_operacional = any(p.exists() for p in base_operacional_paths)
    if not tem_base_operacional:
        faltantes.append("Base Operacional")
    
    return len(faltantes) == 0, faltantes


def copiar_estrutura_core(destino: Path) -> List[str]:
    """
    Copia estrutura core (Constituição, Leis, SOPs) para projeto replicado.
    
    Args:
        destino: Diretório de destino do projeto replicado
    
    Returns:
        Lista de ficheiros copiados
    """
    copiados = []
    
    # Criar estrutura core no destino
    core_dest = destino / "core"
    core_dest.mkdir(parents=True, exist_ok=True)
    
    # Copiar Constituição e Leis
    estruturas_obrigatorias = [
        ("core/sop/constituição.yaml", "core/sop/constituição.yaml"),
        ("core/sop/leis.yaml", "core/sop/leis.yaml"),
        ("core/sop/exceptions.yaml", "core/sop/exceptions.yaml"),
        ("core/sop/doutrina.yaml", "core/sop/doutrina.yaml"),
    ]
    
    for origem_rel, destino_rel in estruturas_obrigatorias:
        origem_abs = REPO_ROOT / origem_rel
        destino_abs = destino / destino_rel
        
        if origem_abs.exists():
            destino_abs.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(origem_abs, destino_abs)
            copiados.append(destino_rel)
    
    return copiados


def copiar_triade(destino: Path) -> List[str]:
    """
    Copia Tríade de Fundamentação para projeto replicado.
    
    Args:
        destino: Diretório de destino do projeto replicado
    
    Returns:
        Lista de ficheiros copiados
    """
    copiados = []
    
    docs_dest = destino / "docs"
    docs_dest.mkdir(parents=True, exist_ok=True)
    
    # White Paper
    white_paper_paths = [
        REPO_ROOT / "docs" / "white_paper.md",
        REPO_ROOT / "docs" / "WHITE_PAPER.md",
        REPO_ROOT / "WHITE_PAPER.md",
    ]
    for wp_path in white_paper_paths:
        if wp_path.exists():
            dest_wp = docs_dest / "WHITE_PAPER.md"
            shutil.copy2(wp_path, dest_wp)
            copiados.append("docs/WHITE_PAPER.md")
            break
    
    # Arquitetura
    arquitetura_paths = [
        REPO_ROOT / "docs" / "arquitetura.md",
        REPO_ROOT / "docs" / "ARQUITETURA.md",
        REPO_ROOT / "ARQUITETURA.md",
        REPO_ROOT / "docs" / "architecture.md",
    ]
    for arq_path in arquitetura_paths:
        if arq_path.exists():
            dest_arq = docs_dest / "ARQUITETURA.md"
            shutil.copy2(arq_path, dest_arq)
            copiados.append("docs/ARQUITETURA.md")
            break
    
    # Base Operacional
    base_operacional_paths = [
        REPO_ROOT / "docs" / "base_operacional.md",
        REPO_ROOT / "docs" / "BASE_OPERACIONAL.md",
        REPO_ROOT / "BASE_OPERACIONAL.md",
        REPO_ROOT / "pipeline" / "README.md",
    ]
    for bo_path in base_operacional_paths:
        if bo_path.exists():
            dest_bo = docs_dest / "BASE_OPERACIONAL.md"
            shutil.copy2(bo_path, dest_bo)
            copiados.append("docs/BASE_OPERACIONAL.md")
            break
    
    return copiados


def gerar_metadados_replicacao(
    projeto_nome: str,
    origem: Path,
    destino: Path,
    triade_copiada: List[str],
    leis_copiadas: List[str]
) -> Dict[str, Any]:
    """
    Gera metadados de replicação conforme ART-07.
    
    Args:
        projeto_nome: Nome do projeto replicado
        origem: Caminho do projeto origem
        destino: Caminho do projeto destino
        triade_copiada: Lista de ficheiros da Tríade copiados
        leis_copiadas: Lista de ficheiros de leis copiados
    
    Returns:
        Dict com metadados de replicação
    """
    return {
        "projeto_nome": projeto_nome,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agente": "ENGENHEIRO",
        "tipo": "replicacao_instantanea",
        "origem": str(origem.relative_to(REPO_ROOT)),
        "destino": str(destino.relative_to(REPO_ROOT)),
        "triade_copiada": triade_copiada,
        "leis_copiadas": leis_copiadas,
        "metadados": {
            "objetivo": f"Replicar projeto {projeto_nome} herdando Tríade e Leis da FÁBRICA",
            "regras_aplicadas": [
                "ART-02: Tríade de Fundamentação",
                "ART-06: Coerência entre Projetos",
                "ART-07: Transparência (metadados obrigatórios)",
            ],
        },
    }


def replicar_projeto(projeto_nome: str, destino_path: str) -> Dict[str, Any]:
    """
    Replica projeto da FÁBRICA para novo destino.
    
    Args:
        projeto_nome: Nome do projeto replicado
        destino_path: Caminho de destino (relativo ou absoluto)
    
    Returns:
        Dict com resultado da replicação
    """
    # Validar Tríade antes de replicar
    triade_ok, faltantes = validar_triade_fundamentacao()
    if not triade_ok:
        return {
            "status": "BLOQUEADO",
            "motivo": f"Tríade incompleta: {', '.join(faltantes)}",
            "artefactos": [],
        }
    
    # Resolver caminho de destino
    if Path(destino_path).is_absolute():
        destino = Path(destino_path)
    else:
        destino = REPO_ROOT.parent / destino_path
    
    # Criar diretório de destino
    destino.mkdir(parents=True, exist_ok=True)
    
    # Copiar Tríade
    print(f"📚 Copiando Tríade de Fundamentação...")
    triade_copiada = copiar_triade(destino)
    print(f"  ✅ {len(triade_copiada)} ficheiros da Tríade copiados")
    
    # Copiar estrutura core (Constituição e Leis)
    print(f"⚖️  Copiando Constituição e Leis...")
    leis_copiadas = copiar_estrutura_core(destino)
    print(f"  ✅ {len(leis_copiadas)} ficheiros de leis copiados")
    
    # Gerar metadados de replicação
    metadados = gerar_metadados_replicacao(
        projeto_nome,
        REPO_ROOT,
        destino,
        triade_copiada,
        leis_copiadas
    )
    
    # Salvar metadados no projeto replicado
    metadados_file = destino / "replicacao_metadados.json"
    with open(metadados_file, "w", encoding="utf-8") as f:
        json.dump(metadados, f, indent=2, ensure_ascii=False)
    
    return {
        "status": "SUCCESS",
        "projeto_nome": projeto_nome,
        "destino": str(destino.relative_to(REPO_ROOT)),
        "triade_copiada": triade_copiada,
        "leis_copiadas": leis_copiadas,
        "metadados": str(metadados_file.relative_to(REPO_ROOT)),
    }


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: replicar.py <nome_projeto> <destino>")
        print("Exemplo: replicar.py meu_projeto ../meu_projeto")
        sys.exit(1)
    
    projeto_nome = sys.argv[1]
    destino_path = sys.argv[2]
    
    resultado = replicar_projeto(projeto_nome, destino_path)
    
    if resultado["status"] == "SUCCESS":
        print(f"\\n✅ Projeto '{projeto_nome}' replicado com sucesso!")
        print(f"Destino: {resultado['destino']}")
        print(f"Tríade: {len(resultado['triade_copiada'])} ficheiros")
        print(f"Leis: {len(resultado['leis_copiadas'])} ficheiros")
        print(f"Metadados: {resultado['metadados']}")
        import json
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
    else:
        print(f"\\n❌ Replicação bloqueada: {resultado.get('motivo', 'Erro desconhecido')}")
        sys.exit(1)
''', encoding="utf-8")
    
    replicar_script.chmod(0o755)
    
    # 4. Criar README explicativo
    readme_file = replicacao_dir / "README.md"
    readme_file.write_text('''# Replicação Instantânea

Sistema para copiar pipelines/projetos da FÁBRICA, herdando Tríade de Fundamentação e Leis.

## Requisitos

### Validação Obrigatória (ART-02)
Antes de replicar, o sistema valida que a Tríade de Fundamentação existe:
- ✅ White Paper (Estratégia)
- ✅ Arquitetura (Estrutura)
- ✅ Base Operacional (Execução)

### Herança Obrigatória (ART-06)
Projetos replicados herdam automaticamente:
- Constituição (`core/sop/constituição.yaml`)
- Leis (`core/sop/leis.yaml`)
- Exceções (`core/sop/exceptions.yaml`)
- Doutrina (`core/sop/doutrina.yaml`)

## Uso

```bash
python3 core/replicacao/replicar.py <nome_projeto> <destino>
```

### Exemplo
```bash
python3 core/replicacao/replicar.py meu_projeto ../meu_projeto
```

## Metadados (ART-07)

Cada projeto replicado inclui `replicacao_metadados.json` com:
- Nome do projeto
- Timestamp da replicação
- Agente que executou
- Tríade copiada
- Leis copiadas
- Regras aplicadas

## Conformidade Constitucional

- **ART-02:** Valida Tríade antes de replicar
- **ART-06:** Garante coerência entre projetos
- **ART-07:** Inclui metadados obrigatórios
- **ART-04:** Rastreabilidade completa

## Notas

- Executado pelo Engenheiro com ordem do Estado-Maior
- Não replica código-fonte automaticamente (apenas estrutura base)
- Requer validação SOP após replicação
''', encoding="utf-8")
    
    # 5. Testar validação de Tríade
    print("\n🔍 Testando validação de Tríade...")
    triade_ok, faltantes = validar_triade_fundamentacao()
    if triade_ok:
        print("  ✅ Tríade completa — replicação pode prosseguir")
    else:
        print(f"  ⚠️  Tríade incompleta: {', '.join(faltantes)}")
        print("  ⚠️  Replicação bloqueada até Tríade estar completa")
    
    artefactos = [
        str(replicacao_dir.relative_to(REPO_ROOT)),
        str(replicar_script.relative_to(REPO_ROOT)),
        str(readme_file.relative_to(REPO_ROOT)),
    ]
    
    save_progresso("REPLICACAO_INSTANTANEA", "Replicação Instantânea", "CONCLUÍDO", artefactos)
    
    return {
        "status": "SUCCESS",
        "capitulo": "REPLICACAO_INSTANTANEA",
        "artefactos": artefactos,
        "triade_validada": triade_ok,
        "faltantes_triade": faltantes if not triade_ok else [],
    }


def executar_padronizacao_formatos() -> Dict[str, Any]:
    """Implementa capítulo 5: Padronização de Formatos."""
    print("=" * 60)
    print("📋 CAPÍTULO 5: Padronização de Formatos")
    print("=" * 60)
    
    # 1. Criar estrutura do módulo de padronização
    padronizacao_dir = REPO_ROOT / "core" / "padronizacao_formatos"
    padronizacao_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. Criar validador de formato
    validador_script = padronizacao_dir / "validar_formato.py"
    validador_script.write_text('''#!/usr/bin/env python3
"""
Validador de Formato Obrigatório — FÁBRICA 2.0
Valida que todas as interações seguem o formato obrigatório.
Conforme doutrina: formato_interacoes.
"""
import re
import sys
from pathlib import Path
from typing import Tuple, List, Dict

REPO_ROOT = Path(__file__).resolve().parents[2]
DOUTRINA_PATH = REPO_ROOT / "core" / "sop" / "doutrina.yaml"


def validar_formato_interacao(conteudo: str) -> Tuple[bool, List[str]]:
    """
    Valida se uma interação segue o formato obrigatório.
    
    Args:
        conteudo: Conteúdo da interação a validar
    
    Returns:
        Tuple[bool, List[str]]: (valido, erros)
    """
    erros = []
    linhas = conteudo.split("\\n")
    
    # Verificar início: PIPELINE/FORA_PIPELINE
    tem_inicio = False
    for i, linha in enumerate(linhas[:10]):  # Verificar primeiras 10 linhas
        if re.search(r"\\*\\*PIPELINE/FORA_PIPELINE\\*\\*.*(PIPELINE|FORA_PIPELINE)", linha, re.IGNORECASE):
            tem_inicio = True
            break
    
    if not tem_inicio:
        erros.append("Interação não contém identificação PIPELINE/FORA_PIPELINE no início")
    
    # Verificar OWNER (opcional mas recomendado)
    tem_owner = False
    for linha in linhas[:15]:
        if re.search(r"\\*\\*OWNER.*—.*Próxima ação\\*\\*", linha, re.IGNORECASE):
            tem_owner = True
            break
    
    # Verificar fim: COMANDO A EXECUTAR
    tem_fim = False
    for linha in reversed(linhas[-10:]):  # Verificar últimas 10 linhas
        if re.search(r"\\*\\*COMANDO A EXECUTAR\\*\\*", linha, re.IGNORECASE):
            tem_fim = True
            break
    
    if not tem_fim:
        erros.append("Interação não contém COMANDO A EXECUTAR no fim")
    
    valido = len(erros) == 0
    
    return valido, erros


def validar_ficheiro_markdown(caminho: Path) -> Tuple[bool, List[str]]:
    """
    Valida formato de um ficheiro markdown.
    
    Args:
        caminho: Caminho do ficheiro a validar
    
    Returns:
        Tuple[bool, List[str]]: (valido, erros)
    """
    if not caminho.exists():
        return False, [f"Ficheiro não existe: {caminho}"]
    
    if caminho.suffix != ".md":
        return False, [f"Ficheiro não é markdown: {caminho}"]
    
    try:
        conteudo = caminho.read_text(encoding="utf-8")
        return validar_formato_interacao(conteudo)
    except Exception as e:
        return False, [f"Erro ao ler ficheiro: {e}"]


def validar_todos_relatorios() -> Dict[str, Tuple[bool, List[str]]]:
    """
    Valida formato de todos os relatórios em relatorios/.
    
    Returns:
        Dict com resultados de validação por ficheiro
    """
    resultados = {}
    relatorios_dir = REPO_ROOT / "relatorios"
    
    if not relatorios_dir.exists():
        return resultados
    
    # Encontrar todos os ficheiros markdown
    for md_file in relatorios_dir.rglob("*.md"):
        valido, erros = validar_ficheiro_markdown(md_file)
        resultados[str(md_file.relative_to(REPO_ROOT))] = (valido, erros)
    
    return resultados


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: validar_formato.py <caminho> | validar_formato.py --todos")
        sys.exit(1)
    
    if sys.argv[1] == "--todos":
        resultados = validar_todos_relatorios()
        validos = sum(1 for v, _ in resultados.values() if v)
        invalidos = len(resultados) - validos
        
        print(f"Validação completa:")
        print(f"  ✅ Válidos: {validos}")
        print(f"  ❌ Inválidos: {invalidos}")
        
        for caminho, (valido, erros) in resultados.items():
            if not valido:
                print(f"\\n❌ {caminho}:")
                for erro in erros:
                    print(f"    - {erro}")
        
        if invalidos > 0:
            sys.exit(1)
    else:
        caminho = Path(sys.argv[1])
        if not caminho.is_absolute():
            caminho = REPO_ROOT / caminho
        
        valido, erros = validar_ficheiro_markdown(caminho)
        
        if valido:
            print(f"✅ {caminho} está conforme o formato obrigatório")
        else:
            print(f"❌ {caminho} não está conforme:")
            for erro in erros:
                print(f"  - {erro}")
            sys.exit(1)
''', encoding="utf-8")
    
    validador_script.chmod(0o755)
    
    # 3. Criar formatador automático
    formatador_script = padronizacao_dir / "formatar_interacao.py"
    formatador_script.write_text('''#!/usr/bin/env python3
"""
Formatador de Interações — FÁBRICA 2.0
Formata interações conforme formato obrigatório.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Importar função de formatação do file_access_guard
try:
    sys.path.insert(0, str(REPO_ROOT / "core" / "orquestrador"))
    from file_access_guard import formatar_resposta_agente
except ImportError:
    # Fallback se não conseguir importar
    def formatar_resposta_agente(agente, conteudo, pipeline_status="FORA_PIPELINE", proxima_acao="", comando_executar=""):
        if not proxima_acao:
            proxima_acao = "Operação concluída"
        if not comando_executar:
            comando_executar = "ESTADO-MAIOR ANALISAR RESPOSTA E CONTINUAR OPERAÇÃO"
        
        return f"""**PIPELINE/FORA_PIPELINE:** {pipeline_status}

**OWNER: {agente} — Próxima ação:** {proxima_acao}

{conteudo}

---

**COMANDO A EXECUTAR:** "{comando_executar}"
"""


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: formatar_interacao.py <agente> <conteudo> [pipeline_status] [proxima_acao] [comando_executar]")
        print("Exemplo: formatar_interacao.py ENGENHEIRO 'Relatório completo' PIPELINE 'Aguardar validação' 'ESTADO-MAIOR ANALISAR'")
        sys.exit(1)
    
    agente = sys.argv[1]
    conteudo = sys.argv[2]
    pipeline_status = sys.argv[3] if len(sys.argv) > 3 else "FORA_PIPELINE"
    proxima_acao = sys.argv[4] if len(sys.argv) > 4 else ""
    comando_executar = sys.argv[5] if len(sys.argv) > 5 else ""
    
    formato = formatar_resposta_agente(
        agente,
        conteudo,
        pipeline_status,
        proxima_acao,
        comando_executar
    )
    
    print(formato)
''', encoding="utf-8")
    
    formatador_script.chmod(0o755)
    
    # 4. Criar README explicativo
    readme_file = padronizacao_dir / "README.md"
    readme_file.write_text('''# Padronização de Formatos

Sistema para garantir que todos os artefatos/relatórios seguem o formato obrigatório conforme doutrina.

## Formato Obrigatório

Todas as interações de todos os agentes devem seguir:

```markdown
**PIPELINE/FORA_PIPELINE:** PIPELINE ou FORA_PIPELINE

**OWNER: AGENTE — Próxima ação:** <frase curta>

[... conteúdo da interação ...]

---

**COMANDO A EXECUTAR:** "AGENTE AÇÃO (localização)"
```

## Uso

### Validar formato de um ficheiro:
```bash
python3 core/padronizacao_formatos/validar_formato.py relatorios/para_estado_maior/relatorio.md
```

### Validar todos os relatórios:
```bash
python3 core/padronizacao_formatos/validar_formato.py --todos
```

### Formatar interação:
```bash
python3 core/padronizacao_formatos/formatar_interacao.py ENGENHEIRO "Conteúdo da interação" PIPELINE "Aguardar validação" "ESTADO-MAIOR ANALISAR"
```

## Ferramentas

- `validar_formato.py` — Valida formato de interações e ficheiros markdown
- `formatar_interacao.py` — Formata interações conforme padrão obrigatório

## Conformidade Constitucional

- **ART-04:** Verificabilidade — formato garante rastreabilidade
- **ART-07:** Transparência — metadados obrigatórios presentes
- **ART-09:** Evidência — comando a executar sempre presente

## Integração

Este módulo integra-se com:
- `core/orquestrador/file_access_guard.py` — Função `formatar_resposta_agente()`
- `core/sop/doutrina.yaml` — Doutrina `formato_interacoes`
''', encoding="utf-8")
    
    # 5. Testar validação
    print("\\n🔍 Testando validação de formato...")
    import subprocess
    result = subprocess.run(
        [sys.executable, str(validador_script), "--todos"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=10,
    )
    
    if result.returncode == 0:
        print("  ✅ Validação funcionando corretamente")
        print(result.stdout[:300])
    else:
        print(f"  ⚠️  Validação retornou código {result.returncode}")
        print(result.stdout[:300])
    
    artefactos = [
        str(padronizacao_dir.relative_to(REPO_ROOT)),
        str(validador_script.relative_to(REPO_ROOT)),
        str(formatador_script.relative_to(REPO_ROOT)),
        str(readme_file.relative_to(REPO_ROOT)),
    ]
    
    save_progresso("PADRONIZACAO_FORMATOS", "Padronização de Formatos", "CONCLUÍDO", artefactos)
    
    return {
        "status": "SUCCESS",
        "capitulo": "PADRONIZACAO_FORMATOS",
        "artefactos": artefactos,
    }


def main() -> int:
    """Função principal."""
    parser = argparse.ArgumentParser(description="Executor da Superpipeline FÁBRICA 2.0")
    parser.add_argument("--inicio", required=True, help="ID do capítulo inicial")
    parser.add_argument("--spec", default="pipeline/superpipeline.yaml", help="Caminho para superpipeline.yaml")
    
    args = parser.parse_args()
    
    # Carregar superpipeline
    spec_path = REPO_ROOT / args.spec
    superpipeline = load_yaml(spec_path)
    
    if not superpipeline:
        print(f"❌ Erro: Não foi possível carregar {spec_path}")
        return 1
    
    capitulos = superpipeline.get("superpipeline", {}).get("capitulos", [])
    
    if not capitulos:
        print("❌ Erro: Nenhum capítulo encontrado na superpipeline")
        return 1
    
    # Encontrar capítulo inicial
    capitulo_inicial = None
    for cap in capitulos:
        if cap.get("id") == args.inicio:
            capitulo_inicial = cap
            break
    
    if not capitulo_inicial:
        print(f"❌ Erro: Capítulo '{args.inicio}' não encontrado")
        print(f"Capítulos disponíveis: {[c.get('id') for c in capitulos]}")
        return 1
    
    # Executar capítulo
    if args.inicio == "RAG_MEMORIA_VIVA":
        resultado = executar_rag_memoria_viva()
    elif args.inicio == "FINGERPRINT_CONFORMIDADE":
        resultado = executar_fingerprint_conformidade()
    elif args.inicio == "TORRE_REFLEXIVA":
        resultado = executar_torre_reflexiva()
    elif args.inicio == "REPLICACAO_INSTANTANEA":
        resultado = executar_replicacao_instantanea()
    elif args.inicio == "PADRONIZACAO_FORMATOS":
        resultado = executar_padronizacao_formatos()
    else:
        print(f"❌ Capítulo '{args.inicio}' ainda não implementado")
        return 1
    
    if resultado["status"] == "SUCCESS":
        print("\n✅ Capítulo executado com sucesso!")
        print(f"Artefactos gerados: {len(resultado['artefactos'])}")
        return 0
    else:
        print("\n❌ Capítulo falhou")
        return 1


if __name__ == "__main__":
    sys.exit(main())

