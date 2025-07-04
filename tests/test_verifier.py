import pytest
import factchecker.verifier as vf
@pytest.mark.asyncio
async def test_verify_claims():
    results = await vf.verify_claims(["ダミー主張"])
    assert results[0]["verdict"].startswith("SUPPORTED")
    assert len(results[0]["sources"]) == 5
