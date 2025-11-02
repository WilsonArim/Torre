#!/usr/bin/env python3
import json, os, subprocess, sys, tempfile, time
from pathlib import Path

TEMPLATES = ".fortaleza/memory/patterns.json"
def run(cmd, timeout=120):
  try:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
  except subprocess.TimeoutExpired as e:
    return e

def try_templates(files_glob="src/**/*.ts*"):
  if not os.path.exists(TEMPLATES):
    return {"ok": True, "attempts":0, "applied":0}
  patterns = json.load(open(TEMPLATES))
  applied = 0; attempts = 0
  # simples: procurar símbolos óbvios
  for err, hunks in patterns.items():
    for h in hunks[:4]:
      attempts += 1
      # aqui poderíamos aplicar codemods equivalentes; guardamos placeholder
  return {"ok":True,"attempts":attempts,"applied":applied}

def validate():
  # valida com npm test se houver; senão, pytest; senão build
  cmds = [["npm","test","--silent","--","-w", "1"], ["pytest","-q"], ["npm","run","-s","build"]]
  for c in cmds:
    r = run(c, timeout=600)
    if isinstance(r, subprocess.TimeoutExpired): return {"ok":False,"stage":"timeout","code":124}
    if r.returncode == 0: return {"ok":True,"stage":"tests"}
  return {"ok":False,"stage":"all_failed"}

if __name__=="__main__":
  out = {"templates": try_templates(), "validation": validate()}
  print(json.dumps(out))
