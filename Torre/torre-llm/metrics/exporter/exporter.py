#!/usr/bin/env python3
import os, json, time
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Iterable, Tuple
from prometheus_client import REGISTRY, GaugeMetricFamily, CounterMetricFamily, start_http_server

METRICS_FILE = os.environ.get("METRICS_FILE", ".metrics")
# Janelas úteis (pode ajustar via env se quiser)
WINDOWS = os.environ.get("WINDOWS", "5m,1h,24h").split(",")

def _parse_ts(ts: str) -> datetime:
    # espera ISO8601 com 'Z'
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return datetime.now(timezone.utc)

def _parse_line(line: str) -> Dict[str, Any]:
    try:
        return json.loads(line)
    except Exception:
        return {}

def _window_bounds(now: datetime, win: str) -> datetime:
    if win.endswith("m"):
        return now - timedelta(minutes=int(win[:-1]))
    if win.endswith("h"):
        return now - timedelta(hours=int(win[:-1]))
    if win.endswith("d"):
        return now - timedelta(days=int(win[:-1]))
    # fallback
    return now - timedelta(hours=1)

def _safe_int(x) -> int:
    try:
        return int(x)
    except Exception:
        return 0

class FixerMetricsCollector:
    """
    Lê .metrics (JSONL) a cada coleta e produz:
      - fortaleza_fixer_runs_total (counter cumulativa baseada no arquivo)
      - fortaleza_fixer_events_total{step} (counter cumulativa)
      - fortaleza_fixer_latest{step} (gauge último valor)
      - fortaleza_fixer_window_sum{step,window} (gauge soma por janela: 5m/1h/24h)
      - fortaleza_fixer_duration_ms (última duração)
      - fortaleza_fixer_files_changed (último valor)
      - fortaleza_fixer_codemods_edits_total{codemod} (counter cumulativa)
    """
    def collect(self) -> Iterable:
        now = datetime.now(timezone.utc)
        runs_total = 0

        # counters cumulativos
        events_total = {
            "ts_codefix_resolved": 0,
            "eslint_resolved": 0,
            "semgrep_resolved": 0,
            "codemods_edits": 0,
        }
        codemods_total: Dict[str, int] = {}

        # latest (do último run)
        latest = {
            "ts_codefix_resolved": 0,
            "eslint_resolved": 0,
            "semgrep_resolved": 0,
            "codemods_edits": 0,
        }
        latest_duration_ms = 0
        latest_files_changed = 0

        # janelas
        window_sums: Dict[str, Dict[str, int]] = {w: {
            "ts_codefix_resolved": 0, "eslint_resolved": 0,
            "semgrep_resolved": 0, "codemods_edits": 0
        } for w in WINDOWS}

        try:
            with open(METRICS_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except FileNotFoundError:
            lines = []

        for line in lines:
            row = _parse_line(line)
            if not row:
                continue

            runs_total += 1
            ts = _parse_ts(row.get("ts") or "")
            sm = row.get("step_metrics") or {}
            ts_codefix = _safe_int(sm.get("ts_codefix_resolved"))
            eslint = _safe_int(sm.get("eslint_resolved"))
            semgrep = _safe_int(sm.get("semgrep_resolved"))
            codemods = _safe_int(sm.get("codemods_edits"))
            duration = _safe_int(row.get("duration_ms"))
            files_changed = _safe_int(row.get("files_changed"))
            per_codemod = row.get("codemods_per_codemod") or {}

            # cumulativos
            events_total["ts_codefix_resolved"] += ts_codefix
            events_total["eslint_resolved"] += eslint
            events_total["semgrep_resolved"] += semgrep
            events_total["codemods_edits"] += codemods

            for cm_name, cm_val in per_codemod.items():
                codemods_total[cm_name] = codemods_total.get(cm_name, 0) + _safe_int(cm_val)

            # latest (mantém do último válido)
            latest = {
                "ts_codefix_resolved": ts_codefix,
                "eslint_resolved": eslint,
                "semgrep_resolved": semgrep,
                "codemods_edits": codemods,
            }
            latest_duration_ms = duration
            latest_files_changed = files_changed

            # janelas
            for w in WINDOWS:
                cutoff = _window_bounds(now, w)
                if ts >= cutoff:
                    window_sums[w]["ts_codefix_resolved"] += ts_codefix
                    window_sums[w]["eslint_resolved"] += eslint
                    window_sums[w]["semgrep_resolved"] += semgrep
                    window_sums[w]["codemods_edits"] += codemods

        # Export: runs total
        runs = CounterMetricFamily("fortaleza_fixer_runs_total", "Total de execuções (.metrics linhas)", labels=[])
        runs.add_metric([], runs_total); yield runs

        # Export: cumulativos por step
        events = CounterMetricFamily("fortaleza_fixer_events_total", "Total cumulativo resolvido por step", labels=["step"])
        for step, val in events_total.items():
            events.add_metric([step], val)
        yield events

        # Export: latest por step
        latest_g = GaugeMetricFamily("fortaleza_fixer_latest", "Último run (valor por step)", labels=["step"])
        for step, val in latest.items():
            latest_g.add_metric([step], val)
        yield latest_g

        # Export: janela (somas)
        win = GaugeMetricFamily("fortaleza_fixer_window_sum", "Soma por janela (5m/1h/24h)", labels=["step","window"])
        for w, steps in window_sums.items():
            for step, val in steps.items():
                win.add_metric([step, w], val)
        yield win

        # Export: últimos auxiliares
        dur = GaugeMetricFamily("fortaleza_fixer_duration_ms", "Duração do último run em ms", labels=[])
        dur.add_metric([], latest_duration_ms); yield dur

        fc = GaugeMetricFamily("fortaleza_fixer_files_changed", "Arquivos mudados no último run", labels=[])
        fc.add_metric([], latest_files_changed); yield fc

        # Export: codemods por nome (cumulativo)
        cm = CounterMetricFamily("fortaleza_fixer_codemods_edits_total", "Total cumulativo de edits por codemod", labels=["codemod"])
        for name, val in codemods_total.items():
            cm.add_metric([name], val)
        yield cm

if __name__ == "__main__":
    port = int(os.environ.get("EXPORTER_PORT", "9108"))
    start_http_server(port)
    REGISTRY.register(FixerMetricsCollector())
    print(f"[exporter] lendo {METRICS_FILE} | escutando em :{port} (Prometheus /metrics)")
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        pass
