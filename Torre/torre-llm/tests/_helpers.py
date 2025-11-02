import os

STRICT = os.getenv("TEST_PROFILE") == "strict"

def expect_ok(status: int) -> None:
    """Helper de asserção por perfil de teste"""
    if STRICT:
        assert status == 200, f"Expected 200, got {status} (strict mode)"
    else:
        assert status in (200, 422, 503, 429), f"Expected 200/422/503/429, got {status} (smoke mode)"

def expect_auth_required(status: int) -> None:
    """Helper para validar que auth é requerido"""
    # Em FastAPI, validação de parâmetros acontece antes da verificação de auth
    # Então pode retornar 422 (validação) ou 401/403 (auth)
    assert status in (401, 403, 422), f"Expected 401/403/422 (auth required or validation), got {status}"

def expect_rate_limited(status: int) -> None:
    """Helper para validar rate limit"""
    assert status == 429, f"Expected 429 (rate limited), got {status}"
