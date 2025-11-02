#!/usr/bin/env python3
import os, json, subprocess, sys
OPENAPI = os.environ.get("OPENAPI_URL","http://localhost:8765/openapi.json")
CMD = ["schemathesis","run", OPENAPI, "--checks","all", "--hypothesis-max-examples=50", "--report","./.fortaleza/out/schemathesis.json"]
rc = subprocess.call(CMD)
print(json.dumps({"ok": rc==0, "rc": rc, "openapi": OPENAPI}))
sys.exit(0)
