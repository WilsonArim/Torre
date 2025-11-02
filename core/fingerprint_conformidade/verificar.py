#!/usr/bin/env python3
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
