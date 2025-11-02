#!/usr/bin/env python3
import os, json, yaml, sys
from datetime import datetime
from pathlib import Path
ROOT = Path(__file__).parents[2]
ORDERS = ROOT/'ordem'/'ordens'
REPORTS = ROOT/'relatorios'/'para_estado_maior'
ORDER_FILES = ['engineer.in.yaml', 'gatekeeper.in.yaml', 'sop.in.yaml']
REPORT_FILES = ['engineer.out.json', 'gatekeeper.out.json', 'sop.out.json']
MAX_SIZE = 200*1024
viol = []

def fail(msg):
    viol.append(msg)

def check_schema(entry, required):
    return all(k in entry for k in required)

now = datetime.utcnow()
open_orders = {}
order_ids = set()
for fn in ORDER_FILES:
    fp = ORDERS/fn
    if not fp.exists(): continue
    if fp.stat().st_size > MAX_SIZE: fail(f"{fn} excede {MAX_SIZE} bytes")
    arr = []
    with open(fp) as f: arr = yaml.safe_load(f) or []
    for entry in arr:
        if not check_schema(entry,["order_id", "created_at", "expires_at", "status", "from_role", "to_role"]):
            fail(f"Ordem malformada em {fn}: {entry}")
            continue
        order_ids.add(entry['order_id'])
        if entry['status']=="OPEN":
            dt_exp = datetime.strptime(entry['expires_at'][:19], '%Y-%m-%dT%H:%M:%S')
            if now>dt_exp:
                fail(f"Ordem expirada mas ainda OPEN: {entry['order_id']}")
            open_orders[entry['order_id']] = {"file":fn,"expires_at":entry['expires_at']}

report_ids = set()
for fn in REPORT_FILES:
    fp = REPORTS/fn
    if not fp.exists(): continue
    if fp.stat().st_size > MAX_SIZE: fail(f"{fn} excede {MAX_SIZE} bytes")
    arr = []
    with open(fp) as f: arr = json.load(f)
    for entry in arr:
        if not check_schema(entry,["order_id", "report_id", "from_role", "to_role", "started_at", "finished_at", "status"]):
            fail(f"Relatório malformado em {fn}: {entry}")
            continue
        report_ids.add(entry['order_id'])

missing = [oid for oid in open_orders if oid not in report_ids]
if missing:
    for oid in missing:
        fail(f"Ordem aberta ou expirada sem relatório correspondente (order_id={oid})")

if viol:
    for v in viol: print(f"MAILBOX ERROR: {v}",file=sys.stderr)
    sys.exit(1)
print("MAILBOX HEALTH OK")
