import json, sys
for f in sys.argv[1:]:
    with open(f) as file:
        data = json.load(file)
    p95 = data.get("metrics", {}).get("http_req_duration", {}).get("p(95)", None)
    err = data.get("metrics", {}).get("http_req_failed", {}).get("rate", None)
    print(f, "=>", "PASS" if (p95 is not None and err is not None and p95 < 2500 and err < 0.01) else "FAIL", f"p95={p95}", f"err={err}")
