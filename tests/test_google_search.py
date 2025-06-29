import pytest
import factchecker.google_search as gs

@pytest.mark.asyncio
async def test_google_search():
    res = await gs("dummy claim")
    assert len(res) == 5
    assert res[0]["reliability"] == "高"
