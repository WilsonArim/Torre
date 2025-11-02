from __future__ import annotations
import time, json, pathlib
from typing import Dict, Any, List
from dataclasses import dataclass, asdict

@dataclass
class MetricsSnapshot:
    """Snapshot de métricas num momento específico"""
    timestamp: float
    success_rate: float
    ttg_ms: int  # Time to green
    diff_size_mean: float
    diff_size_p95: int
    p95_latency_ms: int
    violations_perf: int
    violations_sec: int
    regressions: int
    human_interventions: int

class MetricsDashboard:
    """
    Painel de métricas para Fase 1.3
    Objetivo: Tracking de success_rate, TTG, diff_size, p95_latency, violations(perf,sec)
    """
    
    def __init__(self, storage_path: str = ".fortaleza/metrics"):
        self.storage_path = pathlib.Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.snapshots: List[MetricsSnapshot] = []
        self.current_session = time.time()
        
    def record_episode(self, 
                      success: bool,
                      ttg_ms: int,
                      diff_size: int,
                      latency_ms: int,
                      violations_perf: int = 0,
                      violations_sec: int = 0,
                      regressions: int = 0,
                      human_interventions: int = 0) -> None:
        """Regista métricas de um episódio"""
        snapshot = MetricsSnapshot(
            timestamp=time.time(),
            success_rate=100.0 if success else 0.0,
            ttg_ms=ttg_ms,
            diff_size_mean=float(diff_size),
            diff_size_p95=diff_size,
            p95_latency_ms=latency_ms,
            violations_perf=violations_perf,
            violations_sec=violations_sec,
            regressions=regressions,
            human_interventions=human_interventions
        )
        
        self.snapshots.append(snapshot)
        self._save_snapshot(snapshot)
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Calcula métricas atuais baseadas nos snapshots"""
        if not self.snapshots:
            return self._empty_metrics()
        
        # Filtra snapshots da sessão atual (últimas 24h)
        current_time = time.time()
        recent_snapshots = [s for s in self.snapshots 
                           if current_time - s.timestamp < 86400]  # 24h
        
        if not recent_snapshots:
            return self._empty_metrics()
        
        # Calcula métricas agregadas
        success_count = sum(1 for s in recent_snapshots if s.success_rate > 0)
        success_rate = (success_count / len(recent_snapshots)) * 100
        
        ttg_values = [s.ttg_ms for s in recent_snapshots]
        diff_sizes = [s.diff_size_mean for s in recent_snapshots]
        latencies = [s.p95_latency_ms for s in recent_snapshots]
        
        return {
            "success_rate": round(success_rate, 2),
            "ttg_mean_ms": round(sum(ttg_values) / len(ttg_values), 2),
            "ttg_p95_ms": self._percentile(ttg_values, 95),
            "diff_size_mean": round(sum(diff_sizes) / len(diff_sizes), 2),
            "diff_size_p95": self._percentile(diff_sizes, 95),
            "latency_p95_ms": self._percentile(latencies, 95),
            "violations_perf_total": sum(s.violations_perf for s in recent_snapshots),
            "violations_sec_total": sum(s.violations_sec for s in recent_snapshots),
            "regressions_total": sum(s.regressions for s in recent_snapshots),
            "human_interventions_total": sum(s.human_interventions for s in recent_snapshots),
            "episodes_count": len(recent_snapshots),
            "session_duration_hours": round((current_time - self.current_session) / 3600, 2)
        }
    
    def _empty_metrics(self) -> Dict[str, Any]:
        """Retorna métricas vazias"""
        return {
            "success_rate": 0.0,
            "ttg_mean_ms": 0.0,
            "ttg_p95_ms": 0,
            "diff_size_mean": 0.0,
            "diff_size_p95": 0,
            "latency_p95_ms": 0,
            "violations_perf_total": 0,
            "violations_sec_total": 0,
            "regressions_total": 0,
            "human_interventions_total": 0,
            "episodes_count": 0,
            "session_duration_hours": 0.0
        }
    
    def _percentile(self, values: List[float], percentile: int) -> int:
        """Calcula percentil de uma lista de valores"""
        if not values:
            return 0
        
        sorted_values = sorted(values)
        index = int((percentile / 100) * len(sorted_values))
        return int(sorted_values[min(index, len(sorted_values) - 1)])
    
    def _save_snapshot(self, snapshot: MetricsSnapshot) -> None:
        """Salva snapshot em ficheiro"""
        snapshot_file = self.storage_path / f"snapshot_{int(snapshot.timestamp)}.json"
        with open(snapshot_file, 'w') as f:
            json.dump(asdict(snapshot), f, indent=2)
    
    def load_snapshots(self) -> None:
        """Carrega snapshots salvos"""
        self.snapshots = []
        for snapshot_file in self.storage_path.glob("snapshot_*.json"):
            try:
                with open(snapshot_file, 'r') as f:
                    data = json.load(f)
                    snapshot = MetricsSnapshot(**data)
                    self.snapshots.append(snapshot)
            except Exception as e:
                print(f"⚠️ Erro ao carregar {snapshot_file}: {e}")
        
        # Ordena por timestamp
        self.snapshots.sort(key=lambda x: x.timestamp)
    
    def generate_dashboard_report(self) -> str:
        """Gera relatório do dashboard"""
        metrics = self.get_current_metrics()
        
        report = f"""
# Dashboard de Métricas - Fase 1.3

## Resumo da Sessão
- **Duração**: {metrics['session_duration_hours']} horas
- **Episódios**: {metrics['episodes_count']} episódios processados

## Métricas-Chave
- **Success Rate**: {metrics['success_rate']}%
- **TTG (média)**: {metrics['ttg_mean_ms']}ms
- **TTG (p95)**: {metrics['ttg_p95_ms']}ms
- **Diff Size (média)**: {metrics['diff_size_mean']} linhas
- **Diff Size (p95)**: {metrics['diff_size_p95']} linhas
- **Latency (p95)**: {metrics['latency_p95_ms']}ms

## Violações e Regressões
- **Violações Performance**: {metrics['violations_perf_total']}
- **Violações Segurança**: {metrics['violations_sec_total']}
- **Regressões**: {metrics['regressions_total']}
- **Intervenções Humanas**: {metrics['human_interventions_total']}

## Status dos Gates
- ✅ **Success Rate**: {'✅' if metrics['success_rate'] >= 90 else '❌'} ({metrics['success_rate']}%)
- ✅ **TTG Controlado**: {'✅' if metrics['ttg_p95_ms'] <= 1000 else '❌'} ({metrics['ttg_p95_ms']}ms)
- ✅ **Diff Size Controlado**: {'✅' if metrics['diff_size_p95'] <= 300 else '❌'} ({metrics['diff_size_p95']} linhas)
- ✅ **Sem Violações Sec**: {'✅' if metrics['violations_sec_total'] == 0 else '❌'} ({metrics['violations_sec_total']})

## Tendências
"""
        
        if len(self.snapshots) >= 2:
            recent = self.snapshots[-10:]  # Últimos 10 snapshots
            if len(recent) >= 2:
                first_sr = recent[0].success_rate
                last_sr = recent[-1].success_rate
                trend = "↗️ Melhorando" if last_sr > first_sr else "↘️ Piorando" if last_sr < first_sr else "➡️ Estável"
                report += f"- **Success Rate**: {trend} ({first_sr}% → {last_sr}%)\n"
        
        return report
    
    def export_metrics(self, format: str = "json") -> str:
        """Exporta métricas em formato específico"""
        metrics = self.get_current_metrics()
        
        if format == "json":
            return json.dumps(metrics, indent=2)
        elif format == "csv":
            return ",".join([str(v) for v in metrics.values()])
        else:
            return str(metrics)
