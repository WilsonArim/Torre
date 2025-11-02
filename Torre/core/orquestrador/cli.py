import datetime
from pathlib import Path

def log_autoexec(agent, gate, acao, status, supervisor="@EstadoMaior"):
    log_path = Path("torre/relatorios/autoexec_log_torre.md")
    ts = datetime.datetime.utcnow().isoformat()
    line = f"{ts}Z | agente={agent} | gate={gate} | ação={acao} | supervisor={supervisor} | status={status}\n"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if log_path.exists() else "w"
    with open(log_path, mode, encoding="utf-8") as f:
        f.write(line)

# Exemplo de uso antes/depois das execuções relevantes:
# log_autoexec(agent, gate, acao, "RUNNING")
# ... código de execução ...
# log_autoexec(agent, gate, acao, "PASS" ou "FAIL")


