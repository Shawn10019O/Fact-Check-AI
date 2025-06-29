import pytest
import types
import asyncio
import os 

os.environ.setdefault("OPENAI_API_KEY", "test-key")
# OpenAI モック
class _FakeChoice:
    def __init__(self, content): self.message = types.SimpleNamespace(content=content, function_call=types.SimpleNamespace(arguments='{"claims": ["テスト主張"]}'))

class _FakeCompletion:
    def __init__(self, arguments_json: str):
        func_call = types.SimpleNamespace(arguments=arguments_json)
        self.choices=[types.SimpleNamespace(message=types.SimpleNamespace(function_call=func_call))]

class _FakeChat:
    async def create(self, **kwargs): return _FakeCompletion("SUPPORTED: 根拠十分")

@pytest.fixture(autouse=True)
def patch_openai(monkeypatch):
    import factchecker.openai_helpers as helpers
    fake_client = types.SimpleNamespace(chat=types.SimpleNamespace(completions=_FakeChat()))
    monkeypatch.setattr(helpers, "client", fake_client)
    monkeypatch.setattr("factchecker.extractor.client", fake_client)
    yield

# Google Custom Search モック
@pytest.fixture(autouse=True)
def patch_google(monkeypatch):
    async def _fake_search(claim):  # 常に同じ5件を返すダミー
        return [{"title": "dummy", "snippet": "dummy", "link": "https://example.com", "reliability": "高", "score": 3}] * 5
    monkeypatch.setattr("factchecker.google_search.google_search", _fake_search)
    yield

# 非同期テストのイベントループ
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
