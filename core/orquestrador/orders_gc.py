#!/usr/bin/env python3
import os, shutil, gzip, json, yaml
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).parents[2]
ORDERS = ROOT/'ordem'/'ordens'
REPORTS = ROOT/'relatorios'/'para_estado_maior'
ARCH_ORDERS = ROOT/'arquivo'/'ordens'
ARCH_REPORTS = ROOT/'arquivo'/'relatorios'
INDEX = ROOT/'relatorios'/'ordens_index.json'

ORDER_FILES = ['engineer.in.yaml', 'gatekeeper.in.yaml', 'sop.in.yaml']
REPORT_FILES = ['engineer.out.json', 'gatekeeper.out.json', 'sop.out.json']
OLDEST_DAYS = 14
MAX_ACTIVE = 50

def is_closed(entry):
    return entry.get('status') in ('CLOSED','EXPIRED','PASS','BLOQUEADO') or entry.get('expired', False)

def load_yaml_append(path):
    arr = []
    with open(path) as f:
        for doc in yaml.safe_load_all(f):
            if isinstance(doc, list):
                arr.extend(doc)
            else:
                arr.append(doc)
    return arr

def rotate_file(inpath, archdir, is_yaml=True):
    arr = load_yaml_append(inpath) if is_yaml else json.load(open(inpath))
    active,newarch = [],[]
    now = datetime.utcnow()
    for entry in arr:
        closed = is_closed(entry)
        expired = False
        if 'expires_at' in entry:
            expires = datetime.strptime(entry['expires_at'][:19], '%Y-%m-%dT%H:%M:%S')
            if now > expires:
                expired = True
        # Rotaciona se fechado, expirado, ou lazily pelo tempo
        if closed or expired or (('created_at' in entry) and now-datetime.strptime(entry['created_at'][:19], '%Y-%m-%dT%H:%M:%S') > timedelta(days=OLDEST_DAYS)):
            entry['status'] = entry.get('status') if closed else 'EXPIRED'
            newarch.append(entry)
        else:
            active.append(entry)
    # mantém últimos MAX_ACTIVE
    active = active[-MAX_ACTIVE:]
    if is_yaml:
        with open(inpath, 'w') as f:
            yaml.dump(active, f, allow_unicode=True, sort_keys=False)
    else:
        json.dump(active, open(inpath,'w'), indent=2)
    if newarch:
        outfile = Path(archdir)/((inpath.name.split(".")[0])+f'-{now.date()}.jsonl.gz')
        with gzip.open(outfile,'at') as gz:
            for e in newarch:
                gz.write(json.dumps(e, ensure_ascii=False)+"\n")

# Rotaciona ordens e relatórios
for fn in ORDER_FILES:
    p = ORDERS/fn
    if p.exists():
        rotate_file(p, ARCH_ORDERS, True)
for fn in REPORT_FILES:
    p = REPORTS/fn
    if p.exists():
        rotate_file(p, ARCH_REPORTS, False)

def index_summary():
    idx = {}
    for col,name,is_yaml,src in [(ORDER_FILES,'ordens',True,ORDERS),(REPORT_FILES,'relatorios',False,REPORTS)]:
        colres = {}
        for f in col:
            p = src/f
            try:
                arr = load_yaml_append(p) if is_yaml else json.load(open(p))
                colres[f] = {'count':len(arr),'last_updated':datetime.fromtimestamp(p.stat().st_mtime).isoformat()}
            except: colres[f] = {'count':0,'last_updated':None}
        idx[name]=colres
    idx['run_at']=datetime.utcnow().isoformat()
    with open(INDEX,'w') as f: json.dump(idx,f,indent=2)

index_summary()
