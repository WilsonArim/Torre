import os, json, subprocess, sys

def run_cli(payload: dict, env: dict):
    p = subprocess.Popen([sys.executable, "-m", "llm.cli"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
    out, err = p.communicate(json.dumps(payload), timeout=10)
    return p.returncode, out, err

def test_cli_providers_optin_smoke():
    payload = {"logs":{"types":"TS2307: Cannot find module ./x.css"}, "files":{"src/App.tsx":"console.log(1)"}}
    env = os.environ.copy()
    env["PROVIDERS_V1"] = "1"
    code, out, err = run_cli(payload, env)
    assert code == 0
    data = json.loads(out or "{}")
    # tolerante: só checa que o bloco providers existe quando opt-in
    prov = (data.get("metrics") or {}).get("providers")
    assert prov is not None
