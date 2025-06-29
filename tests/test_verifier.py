import pytest
from factchecker.verifier import verify_claims

@pytest.mark.asyncio
async def test_verify_claims():
    results = await verify_claims(["ダミー主張"])
    assert results[0]["verdict"].startswith("SUPPORTED")
    assert len(results[0]["sources"]) == 5
