#!/usr/bin/env python3
"""
API Server da Torre LLM
Servidor HTTP para integração com Cursor e outras ferramentas
"""

import json
import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import subprocess
import tempfile
import os
from pathlib import Path
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações
FORTALEZA_ROOT = Path(__file__).parent
API_PORT = int(os.environ.get("FORTALEZA_API_PORT", "8000"))
API_HOST = os.environ.get("FORTALEZA_API_HOST", "0.0.0.0")

# Modelos Pydantic
class ErrorInfo(BaseModel):
    type: str
    code: str
    message: str
    file: str
    line: int
    column: int
    severity: str

class ContextInfo(BaseModel):
    workspace: Dict[str, Any]
    timestamp: str
    cursor_version: str

class FixRequest(BaseModel):
    error: ErrorInfo
    context: ContextInfo

class FixResponse(BaseModel):
    success: bool
    diff: Optional[Dict[str, Any]] = None
    advice: Optional[str] = None
    confidence: float = 0.0
    method: str = "unknown"
    duration_ms: int = 0

# Inicializar FastAPI
app = FastAPI(
    title="Torre LLM API",
    description="API para correção automática de erros de código",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FortalezaAPI:
    def __init__(self):
        self.root_path = FORTALEZA_ROOT
        self.metrics_file = self.root_path / ".metrics"
        self.memory_dir = self.root_path / ".fortaleza" / "memory"
        
        # Garantir que diretórios existem
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Fortaleza API inicializada em {self.root_path}")
    
    async def fix_error(self, request: FixRequest) -> FixResponse:
        """Corrige um erro usando a pipeline da Fortaleza"""
        start_time = datetime.now()
        
        try:
            logger.info(f"Recebido erro: {request.error.code} em {request.error.file}")
            
            # 1. Executar pipeline de correção
            fix_result = await self.run_correction_pipeline(request)
            
            # 2. Calcular duração
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            # 3. Salvar episódio para aprendizagem
            await self.save_episode(request, fix_result, duration)
            
            return FixResponse(
                success=fix_result.get("success", False),
                diff=fix_result.get("diff"),
                advice=fix_result.get("advice"),
                confidence=fix_result.get("confidence", 0.0),
                method=fix_result.get("method", "pipeline"),
                duration_ms=int(duration)
            )
            
        except Exception as e:
            logger.error(f"Erro ao corrigir: {e}")
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            return FixResponse(
                success=False,
                advice=f"Erro interno: {str(e)}",
                duration_ms=int(duration)
            )
    
    async def run_correction_pipeline(self, request: FixRequest) -> Dict[str, Any]:
        """Executa a pipeline de correção"""
        try:
            # 1. Executar pipeline pré-LLM
            pipeline_result = await self.run_pre_llm_pipeline(request)
            
            # 2. Se ainda há erros, usar LLM
            if pipeline_result.get("errors_remaining", 0) > 0:
                llm_result = await self.run_llm_fix(request)
                return llm_result
            else:
                return pipeline_result
                
        except Exception as e:
            logger.error(f"Erro na pipeline: {e}")
            return {"success": False, "error": str(e)}
    
    async def run_pre_llm_pipeline(self, request: FixRequest) -> Dict[str, Any]:
        """Executa pipeline pré-LLM (ferramentas determinísticas)"""
        try:
            # Executar make pre-llm
            result = subprocess.run(
                ["make", "pre-llm"],
                cwd=self.root_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                # Verificar se o erro foi corrigido
                errors_remaining = await self.check_errors_remaining(request)
                
                return {
                    "success": errors_remaining == 0,
                    "method": "pipeline",
                    "confidence": 0.9 if errors_remaining == 0 else 0.3,
                    "errors_remaining": errors_remaining,
                    "advice": "Pipeline de correção automática aplicada"
                }
            else:
                return {
                    "success": False,
                    "method": "pipeline",
                    "error": result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "method": "pipeline",
                "error": "Timeout na execução da pipeline"
            }
        except Exception as e:
            return {
                "success": False,
                "method": "pipeline",
                "error": str(e)
            }
    
    async def run_llm_fix(self, request: FixRequest) -> Dict[str, Any]:
        """Executa correção via LLM"""
        try:
            # Preparar input para LLM
            llm_input = self.prepare_llm_input(request)
            
            # Executar LLM
            result = subprocess.run(
                ["python3", "-m", "fortaleza-llm.llm.cli"],
                cwd=self.root_path,
                input=json.dumps(llm_input),
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                try:
                    llm_output = json.loads(result.stdout)
                    return {
                        "success": llm_output.get("success", False),
                        "diff": llm_output.get("diff"),
                        "method": "llm",
                        "confidence": llm_output.get("confidence", 0.7)
                    }
                except json.JSONDecodeError:
                    return {
                        "success": False,
                        "method": "llm",
                        "error": "Resposta inválida da LLM"
                    }
            else:
                return {
                    "success": False,
                    "method": "llm",
                    "error": result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "method": "llm",
                "error": "Timeout na execução da LLM"
            }
        except Exception as e:
            return {
                "success": False,
                "method": "llm",
                "error": str(e)
            }
    
    def prepare_llm_input(self, request: FixRequest) -> Dict[str, Any]:
        """Prepara input para a LLM"""
        return {
            "error": {
                "type": request.error.type,
                "code": request.error.code,
                "message": request.error.message,
                "file": request.error.file,
                "line": request.error.line,
                "column": request.error.column
            },
            "context": {
                "workspace": request.context.workspace,
                "timestamp": request.context.timestamp
            },
            "mode": "fix"
        }
    
    async def check_errors_remaining(self, request: FixRequest) -> int:
        """Verifica quantos erros ainda existem"""
        try:
            # Executar verificação rápida
            result = subprocess.run(
                ["npx", "tsc", "--noEmit"],
                cwd=self.root_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Contar erros no output
            error_lines = [line for line in result.stderr.split('\n') if 'error TS' in line]
            return len(error_lines)
            
        except Exception:
            return 1  # Assumir que ainda há erros
    
    async def save_episode(self, request: FixRequest, result: Dict[str, Any], duration: float):
        """Salva episódio para aprendizagem"""
        try:
            episode = {
                "timestamp": datetime.now().isoformat(),
                "error_code": request.error.code,
                "error_message": request.error.message,
                "file": request.error.file,
                "success": result.get("success", False),
                "method": result.get("method", "unknown"),
                "duration_ms": int(duration),
                "confidence": result.get("confidence", 0.0),
                "workspace": request.context.workspace.get("name", "unknown")
            }
            
            # Salvar em episodes.jsonl
            episodes_file = self.memory_dir / "episodes.jsonl"
            with open(episodes_file, "a") as f:
                f.write(json.dumps(episode) + "\n")
                
            logger.info(f"Episódio salvo: {episode['error_code']} -> {episode['success']}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar episódio: {e}")

# Instanciar API
fortaleza_api = FortalezaAPI()

# Rotas da API
@app.post("/fix", response_model=FixResponse)
async def fix_error(request: FixRequest):
    """Corrige um erro de código"""
    return await fortaleza_api.fix_error(request)

@app.get("/health")
async def health_check():
    """Verifica saúde da API"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/metrics")
async def get_metrics():
    """Retorna métricas da Fortaleza"""
    try:
        if fortaleza_api.metrics_file.exists():
            with open(fortaleza_api.metrics_file, "r") as f:
                lines = f.readlines()
                return {
                    "total_runs": len(lines),
                    "last_run": lines[-1] if lines else None
                }
        else:
            return {"total_runs": 0, "last_run": None}
    except Exception as e:
        return {"error": str(e)}

@app.post("/config")
async def update_config(config: Dict[str, Any]):
    """Atualiza configuração da API"""
    # Implementar atualização de configuração
    return {"status": "updated", "config": config}

# Middleware para logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.now()
    response = await call_next(request)
    duration = (datetime.now() - start_time).total_seconds() * 1000
    
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {duration:.2f}ms")
    
    return response

# Tratamento de erros
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Erro não tratado: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Erro interno do servidor", "detail": str(exc)}
    )

if __name__ == "__main__":
    logger.info(f"Iniciando Fortaleza API em {API_HOST}:{API_PORT}")
    uvicorn.run(
        "api_server:app",
        host=API_HOST,
        port=API_PORT,
        reload=True,
        log_level="info"
    )
