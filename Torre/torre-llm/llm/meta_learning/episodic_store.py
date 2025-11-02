from __future__ import annotations
import json, sqlite3, hashlib, time, pathlib
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import re

@dataclass
class Episode:
    """Episódio de aprendizagem"""
    episode_id: str
    timestamp: float
    error_signature: str
    context_hash: str
    tactic_applied: str
    success_delta: float  # -1 a 1 (falha a sucesso)
    confidence: float
    diff_size: int
    ttg_ms: int
    metadata: Dict[str, Any]

@dataclass
class Lesson:
    """Lição aprendida de episódios"""
    lesson_id: str
    error_signature: str
    context_hash: str
    tactic_applied: str
    success_rate: float
    confidence: float
    last_seen: float
    decay_half_life_days: float
    application_count: int
    metadata: Dict[str, Any]

class EpisodicStore:
    """
    Episodic Store: armazena episódios de aprendizagem sem PII
    Objetivo: reduzir erros repetidos através de lições aprendidas
    """
    
    def __init__(self, workspace_path: str = "."):
        self.workspace_path = pathlib.Path(workspace_path)
        self.episodes_dir = self.workspace_path / ".fortaleza" / "episodes"
        self.lessons_db = self.workspace_path / ".fortaleza" / "lessons" / "lessons.sqlite"
        
        # Cria diretórios se não existirem
        self.episodes_dir.mkdir(parents=True, exist_ok=True)
        self.lessons_db.parent.mkdir(parents=True, exist_ok=True)
        
        # Inicializa banco de dados
        self._init_database()
        
        # Configurações
        self.config = {
            "max_episodes_per_file": 1000,
            "max_lessons_active": 100,
            "min_confidence": 0.6,
            "decay_half_life_days": 30.0,
            "success_threshold": 0.7
        }
    
    def _init_database(self) -> None:
        """Inicializa banco de dados SQLite"""
        with sqlite3.connect(self.lessons_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS lessons (
                    lesson_id TEXT PRIMARY KEY,
                    error_signature TEXT NOT NULL,
                    context_hash TEXT NOT NULL,
                    tactic_applied TEXT NOT NULL,
                    success_rate REAL NOT NULL,
                    confidence REAL NOT NULL,
                    last_seen REAL NOT NULL,
                    decay_half_life_days REAL NOT NULL,
                    application_count INTEGER DEFAULT 0,
                    metadata TEXT,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_error_signature 
                ON lessons(error_signature)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_context_hash 
                ON lessons(context_hash)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_confidence 
                ON lessons(confidence DESC)
            """)
    
    def store_episode(self, 
                     error_signature: str,
                     context: Dict[str, Any],
                     tactic_applied: str,
                     success: bool,
                     diff_size: int,
                     ttg_ms: int,
                     metadata: Dict[str, Any] = None) -> str:
        """Armazena um episódio de aprendizagem"""
        
        # Gera ID único
        episode_id = self._generate_episode_id(error_signature, context)
        
        # Calcula context hash (sem PII)
        context_hash = self._hash_context(context)
        
        # Calcula success delta
        success_delta = 1.0 if success else -1.0
        
        # Cria episódio
        episode = Episode(
            episode_id=episode_id,
            timestamp=time.time(),
            error_signature=error_signature,
            context_hash=context_hash,
            tactic_applied=tactic_applied,
            success_delta=success_delta,
            confidence=metadata.get("confidence", 0.5) if metadata else 0.5,
            diff_size=diff_size,
            ttg_ms=ttg_ms,
            metadata=metadata or {}
        )
        
        # Salva em arquivo JSONL
        self._save_episode_to_file(episode)
        
        # Atualiza lições
        self._update_lessons_from_episode(episode)
        
        return episode_id
    
    def _generate_episode_id(self, error_signature: str, context: Dict[str, Any]) -> str:
        """Gera ID único para episódio"""
        content = f"{error_signature}:{self._hash_context(context)}:{time.time()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _hash_context(self, context: Dict[str, Any]) -> str:
        """Gera hash do contexto sem PII"""
        # Remove PII e segredos
        safe_context = self._sanitize_context(context)
        
        # Converte para string e gera hash
        context_str = json.dumps(safe_context, sort_keys=True)
        return hashlib.sha256(context_str.encode()).hexdigest()[:16]
    
    def _sanitize_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Remove PII e segredos do contexto"""
        safe_context = {}
        
        for key, value in context.items():
            if key in ["files", "error_logs", "priority", "framework", "stack"]:
                # Mantém informações seguras
                if key == "error_logs":
                    # Redige erros específicos, mantém padrões
                    safe_logs = []
                    for log in value:
                        # Remove paths específicos, mantém tipos de erro
                        sanitized = re.sub(r'[\/\\][^\s\/\\]+\.(ts|js|py)', '/file.ext', log)
                        sanitized = re.sub(r'[A-Za-z0-9]{32,}', '[REDACTED]', sanitized)
                        safe_logs.append(sanitized)
                    safe_context[key] = safe_logs
                else:
                    safe_context[key] = value
        
        return safe_context
    
    def _save_episode_to_file(self, episode: Episode) -> None:
        """Salva episódio em arquivo JSONL"""
        # Determina arquivo baseado na data
        date_str = datetime.fromtimestamp(episode.timestamp).strftime("%Y-%m-%d")
        episode_file = self.episodes_dir / f"episodes_{date_str}.jsonl"
        
        # Adiciona episódio ao arquivo
        with open(episode_file, 'a') as f:
            f.write(json.dumps(asdict(episode)) + '\n')
    
    def _update_lessons_from_episode(self, episode: Episode) -> None:
        """Atualiza lições baseado no episódio"""
        with sqlite3.connect(self.lessons_db) as conn:
            # Procura lição existente
            cursor = conn.execute("""
                SELECT lesson_id, success_rate, confidence, application_count, last_seen
                FROM lessons 
                WHERE error_signature = ? AND context_hash = ? AND tactic_applied = ?
            """, (episode.error_signature, episode.context_hash, episode.tactic_applied))
            
            existing = cursor.fetchone()
            
            if existing:
                # Atualiza lição existente
                lesson_id, old_success_rate, old_confidence, old_count, old_last_seen = existing
                
                # Calcula nova success rate (média ponderada)
                new_count = old_count + 1
                new_success_rate = ((old_success_rate * old_count) + 
                                  (1.0 if episode.success_delta > 0 else 0.0)) / new_count
                
                # Atualiza confiança baseado no tempo
                time_decay = self._calculate_time_decay(episode.timestamp, old_last_seen)
                new_confidence = (old_confidence * time_decay + episode.confidence) / (time_decay + 1)
                
                conn.execute("""
                    UPDATE lessons 
                    SET success_rate = ?, confidence = ?, application_count = ?, 
                        last_seen = ?, updated_at = ?
                    WHERE lesson_id = ?
                """, (new_success_rate, new_confidence, new_count, 
                     episode.timestamp, time.time(), lesson_id))
            else:
                # Cria nova lição
                lesson_id = hashlib.sha256(
                    f"{episode.error_signature}:{episode.context_hash}:{episode.tactic_applied}".encode()
                ).hexdigest()[:16]
                
                success_rate = 1.0 if episode.success_delta > 0 else 0.0
                
                conn.execute("""
                    INSERT INTO lessons (
                        lesson_id, error_signature, context_hash, tactic_applied,
                        success_rate, confidence, last_seen, decay_half_life_days,
                        application_count, metadata, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    lesson_id, episode.error_signature, episode.context_hash,
                    episode.tactic_applied, success_rate, episode.confidence,
                    episode.timestamp, self.config["decay_half_life_days"],
                    1, json.dumps(episode.metadata), time.time(), time.time()
                ))
    
    def _calculate_time_decay(self, current_time: float, last_time: float) -> float:
        """Calcula decaimento temporal"""
        days_diff = (current_time - last_time) / (24 * 3600)
        half_life = self.config["decay_half_life_days"]
        return 2 ** (-days_diff / half_life)
    
    def get_relevant_lessons(self, 
                           error_signature: str,
                           context: Dict[str, Any],
                           limit: int = 5) -> List[Lesson]:
        """Retorna lições relevantes para um erro"""
        
        context_hash = self._hash_context(context)
        
        with sqlite3.connect(self.lessons_db) as conn:
            # Procura lições por assinatura e contexto
            cursor = conn.execute("""
                SELECT lesson_id, error_signature, context_hash, tactic_applied,
                       success_rate, confidence, last_seen, decay_half_life_days,
                       application_count, metadata
                FROM lessons 
                WHERE error_signature = ? 
                AND confidence >= ?
                ORDER BY confidence DESC, success_rate DESC
                LIMIT ?
            """, (error_signature, self.config["min_confidence"], limit))
            
            lessons = []
            for row in cursor.fetchall():
                lesson = Lesson(
                    lesson_id=row[0],
                    error_signature=row[1],
                    context_hash=row[2],
                    tactic_applied=row[3],
                    success_rate=row[4],
                    confidence=row[5],
                    last_seen=row[6],
                    decay_half_life_days=row[7],
                    application_count=row[8],
                    metadata=json.loads(row[9]) if row[9] else {}
                )
                lessons.append(lesson)
            
            return lessons
    
    def get_lesson_by_id(self, lesson_id: str) -> Optional[Lesson]:
        """Retorna lição por ID"""
        with sqlite3.connect(self.lessons_db) as conn:
            cursor = conn.execute("""
                SELECT lesson_id, error_signature, context_hash, tactic_applied,
                       success_rate, confidence, last_seen, decay_half_life_days,
                       application_count, metadata
                FROM lessons 
                WHERE lesson_id = ?
            """, (lesson_id,))
            
            row = cursor.fetchone()
            if row:
                return Lesson(
                    lesson_id=row[0],
                    error_signature=row[1],
                    context_hash=row[2],
                    tactic_applied=row[3],
                    success_rate=row[4],
                    confidence=row[5],
                    last_seen=row[6],
                    decay_half_life_days=row[7],
                    application_count=row[8],
                    metadata=json.loads(row[9]) if row[9] else {}
                )
            return None
    
    def get_lessons_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas das lições"""
        with sqlite3.connect(self.lessons_db) as conn:
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_lessons,
                    AVG(success_rate) as avg_success_rate,
                    AVG(confidence) as avg_confidence,
                    SUM(application_count) as total_applications
                FROM lessons
            """)
            
            row = cursor.fetchone()
            return {
                "total_lessons": row[0],
                "avg_success_rate": row[1] or 0.0,
                "avg_confidence": row[2] or 0.0,
                "total_applications": row[3] or 0
            }
    
    def cleanup_old_lessons(self, days_threshold: int = 90) -> int:
        """Remove lições antigas e de baixa confiança"""
        cutoff_time = time.time() - (days_threshold * 24 * 3600)
        
        with sqlite3.connect(self.lessons_db) as conn:
            cursor = conn.execute("""
                DELETE FROM lessons 
                WHERE last_seen < ? OR confidence < ?
            """, (cutoff_time, self.config["min_confidence"]))
            
            return cursor.rowcount
    
    def purge_lessons_by_signature(self, error_signature: str) -> int:
        """Remove lições por assinatura de erro"""
        with sqlite3.connect(self.lessons_db) as conn:
            cursor = conn.execute("""
                DELETE FROM lessons 
                WHERE error_signature = ?
            """, (error_signature,))
            
            return cursor.rowcount
