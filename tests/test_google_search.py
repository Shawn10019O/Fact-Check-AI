import pytest
from factchecker.google_search import google_search

@pytest.mark.asyncio
async def test_google_search():
    res = await google_search("dummy claim")
    assert len(res) == 5
    assert res[0]["reliability"] == "高"
