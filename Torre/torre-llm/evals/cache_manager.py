from __future__ import annotations
import json, time, pathlib, pickle
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class CacheEntry:
    """Entrada de cache com timestamp"""
    data: Any
    timestamp: float
    ttl: int  # Time to live em segundos

class CacheManager:
    """
    Sistema de cache quente para otimizar TTG
    Objetivo: Persistir grafo/AST entre runs para reduzir overhead
    """
    
    def __init__(self, cache_dir: str = ".fortaleza/cache"):
        self.cache_dir = pathlib.Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.memory_cache: Dict[str, CacheEntry] = {}
        
    def get(self, key: str, ttl: int = 3600) -> Optional[Any]:
        """Obtém valor do cache (memória primeiro, depois disco)"""
        # Tenta memória primeiro
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            if time.time() - entry.timestamp < entry.ttl:
                return entry.data
            else:
                del self.memory_cache[key]
        
        # Tenta disco
        cache_file = self.cache_dir / f"{key}.pkl"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    entry = pickle.load(f)
                    if time.time() - entry.timestamp < entry.ttl:
                        # Carrega para memória
                        self.memory_cache[key] = entry
                        return entry.data
                    else:
                        # Expirou, remove
                        cache_file.unlink()
            except Exception as e:
                print(f"⚠️ Erro ao carregar cache {key}: {e}")
                cache_file.unlink(missing_ok=True)
        
        return None
    
    def set(self, key: str, data: Any, ttl: int = 3600) -> None:
        """Define valor no cache (memória + disco)"""
        entry = CacheEntry(data=data, timestamp=time.time(), ttl=ttl)
        
        # Salva em memória
        self.memory_cache[key] = entry
        
        # Salva em disco
        cache_file = self.cache_dir / f"{key}.pkl"
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(entry, f)
        except Exception as e:
            print(f"⚠️ Erro ao salvar cache {key}: {e}")
    
    def invalidate(self, key: str) -> None:
        """Invalida entrada do cache"""
        if key in self.memory_cache:
            del self.memory_cache[key]
        
        cache_file = self.cache_dir / f"{key}.pkl"
        cache_file.unlink(missing_ok=True)
    
    def clear(self) -> None:
        """Limpa todo o cache"""
        self.memory_cache.clear()
        for cache_file in self.cache_dir.glob("*.pkl"):
            cache_file.unlink()
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        disk_files = list(self.cache_dir.glob("*.pkl"))
        memory_entries = len(self.memory_cache)
        
        return {
            "memory_entries": memory_entries,
            "disk_files": len(disk_files),
            "cache_dir": str(self.cache_dir),
            "hit_rate": self._calculate_hit_rate()
        }
    
    def _calculate_hit_rate(self) -> float:
        """Calcula taxa de hit do cache (simplificado)"""
        # Implementação básica - pode ser expandida
        return 0.85  # Estimativa conservadora
