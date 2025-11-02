from __future__ import annotations
import time
from typing import Optional
from ..base import Provider, ProviderRequest, ProviderResponse, _est_tokens, make_noop_diff

class LocalStub(Provider):
    name = "local/qwen2.5-7b"
    def generate(self, req: ProviderRequest) -> ProviderResponse:
        t0 = time.time()
        # gera um patch minimalista e seguro
        first = next(iter(req.files.keys()), "app.ts")
        diff = f"--- a/{first}\n+++ b/{first}\n+// local: quick refactor stub\n"
        return ProviderResponse(
            provider=self.name,
            diff=diff,
            tokens_in=_est_tokens(str(req.logs) + "".join(req.files.values())),
            tokens_out=_est_tokens(diff),
            latency_ms=int((time.time() - t0) * 1000),
            meta={"hint":"low-cost/refactor"}
        )
