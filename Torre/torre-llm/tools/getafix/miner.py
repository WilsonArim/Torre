#!/usr/bin/env python3
# Lê .fortaleza/memory/episodes.jsonl e minera "edit patterns" simples (diff hunks) por código de erro.
import json, re, sys, os
from collections import defaultdict, Counter
EP_FILE = ".fortaleza/memory/episodes.jsonl"
OUT_FILE = ".fortaleza/memory/patterns.json"

def normalize_hunk(h):
  # remove nomes e números muito específicos
  h = re.sub(r'([A-Za-z_][A-Za-z0-9_]{2,})', '<ID>', h)
  h = re.sub(r'\b\d+\b', '<NUM>', h)
  return h

def main():
  if not os.path.exists(EP_FILE):
    print(json.dumps({"ok":True,"patterns":0,"note":"no episodes"})); return
  pats = defaultdict(Counter)
  with open(EP_FILE) as f:
    for line in f:
      try:
        ep = json.loads(line)
      except: 
        continue
      err = ep.get("err_code") or ep.get("error_code") or "UNKNOWN"
      diff = ep.get("diff") or ep.get("patch") or ""
      for h in re.findall(r'(^@@.*?$\n(?:[ +\-].*?\n)+)', diff, flags=re.M|re.S):
        pats[err][normalize_hunk(h)] += 1
  top = {k: [h for h,_ in v.most_common(8)] for k,v in pats.items()}
  os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
  with open(OUT_FILE,"w") as f: json.dump(top,f,indent=2)
  print(json.dumps({"ok":True,"rules":sum(len(v) for v in top.values())}))
if __name__=="__main__": main()
