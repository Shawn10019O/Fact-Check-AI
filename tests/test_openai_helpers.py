import pytest
from factchecker.openai_helpers import bullets_to_sentences

@pytest.mark.asyncio
async def test_bullets_to_sentences():
    sents = await bullets_to_sentences(["例 bullet"])
    assert sents == ["テスト主張"]
