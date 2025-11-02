#!/usr/bin/env python3
"""
API Simplificada da Torre para Teste
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn

app = FastAPI(title="Torre API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "service": "Torre API"
    }

@app.post("/editor/patch")
async def editor_patch(request: dict):
    """Endpoint para correção automática"""
    return {
        "mode": "AUTO",
        "diff": "console.log('Hello World');",  # Exemplo de correção
        "files_out": {
            "test.js": "console.log('Hello World');"
        },
        "metrics": {"confidence": 0.95},
        "report": {"fixed": True},
        "trace_id": "test-123"
    }

@app.get("/")
async def root():
    return {"message": "Torre API está funcionando!"}

if __name__ == "__main__":
    print("🚀 Iniciando Torre API...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
