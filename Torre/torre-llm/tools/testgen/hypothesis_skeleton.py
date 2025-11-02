# Gera esqueleto de property tests para funções puras detectadas rapidamente.
import inspect, importlib, sys, json, os
from pathlib import Path
TGT = os.environ.get("PY_MODULE","app.utils")  # ajusta no uso
mod = importlib.import_module(TGT)
tests=[]
for name, fn in inspect.getmembers(mod, inspect.isfunction):
    src = inspect.getsource(fn)
    if "requests" in src or "os." in src: 
        continue
    tests.append(f"""
from hypothesis import given, strategies as st
from {TGT} import {name}
def test_{name}_no_crash():
    # TODO: refinar geradores conforme assinatura
    {name}(*[])
""")
Path("tests/generated").mkdir(parents=True, exist_ok=True)
Path(f"tests/generated/test_{TGT.replace('.','_')}_props.py").write_text("\\n".join(tests))
print(json.dumps({"ok":True,"generated":len(tests)}))
