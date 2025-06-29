import asyncio
from typing import List, Dict
from googleapiclient.discovery import build
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential_jitter,
    retry_if_exception_type,
)
import os
from factchecker.reliability import get_source_reliability

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
CUSTOM_SEARCH_ENGINE_ID = os.getenv("CUSTOM_SEARCH_ENGINE_ID")
MAX_SOURCES = 5 

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential_jitter(initial=1, max=10),
    retry=retry_if_exception_type(Exception),
)
async def google_search(claim: str) -> List[Dict]:
    def _sync_search() -> List[Dict]:
        service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
        res = (
            service.cse()
            .list(q=claim, cx=CUSTOM_SEARCH_ENGINE_ID, num=10, hl="ja")
            .execute()
        )
        items = res.get("items", [])
        results = []
        for it in items:
            url = it["link"]
            if not url.startswith("https://"):
                continue
            reliability, score = get_source_reliability(url)
            results.append(
                {
                    "title": it["title"],
                    "snippet": it.get("snippet", ""),
                    "link": url,
                    "reliability": reliability,
                    "score": score,
                }
            )
        # スコア順に上位 MAX_SOURCES 件
        return sorted(results, key=lambda x: x["score"], reverse=True)[:MAX_SOURCES]

    return await asyncio.to_thread(_sync_search)