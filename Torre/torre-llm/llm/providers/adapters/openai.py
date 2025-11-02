from __future__ import annotations
import time
from ..base import Provider, ProviderRequest, ProviderResponse, _est_tokens, make_noop_diff

class OpenAIStub(Provider):
    name = "openai/gpt-4o"
    def generate(self, req: ProviderRequest) -> ProviderResponse:
        t0 = time.time()
        # foca em precisão/estrutura (ex.: types/tests/docs)
        first = next(iter(req.files.keys()), "app.ts")
        diff = f"--- a/{first}\n+++ b/{first}\n+// gpt: precise fix stub\n"
        return ProviderResponse(
            provider=self.name,
            diff=diff,
            tokens_in=_est_tokens(str(req.logs) + "".join(req.files.values())),
            tokens_out=_est_tokens(diff),
            latency_ms=int((time.time() - t0) * 1000),
            meta={"strength":"precision"}
        )
