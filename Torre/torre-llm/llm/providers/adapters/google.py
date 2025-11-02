from __future__ import annotations
import time
from ..base import Provider, ProviderRequest, ProviderResponse, _est_tokens

class GoogleStub(Provider):
    name = "google/gemini-1.5"
    def generate(self, req: ProviderRequest) -> ProviderResponse:
        t0 = time.time()
        # bom para multimodal/assets; aqui apenas stub textual
        first = next(iter(req.files.keys()), "app.ts")
        diff = f"--- a/{first}\n+++ b/{first}\n+// gemini: assets/multimodal stub\n"
        return ProviderResponse(
            provider=self.name,
            diff=diff,
            tokens_in=_est_tokens(str(req.logs) + "".join(req.files.values())),
            tokens_out=_est_tokens(diff),
            latency_ms=int((time.time() - t0) * 1000),
            meta={"strength":"multimodal"}
        )
