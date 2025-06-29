import asyncio
from typing import List, Dict
from google_search import google_search
from openai_helpers import openai_chat


async def evidence_based_verdict(claim: str, sources: List[Dict]) -> str:
    # ❶ 証拠を整形（タイトル＋スニペット＋URL）
    evidence_lines = []
    for i, s in enumerate(sources, 1):
        evidence_lines.append(
            f"{i}. [{s['reliability']}] {s['title']} — {s['snippet']} ({s['link']})"
        )
    evidence_txt = "\n".join(evidence_lines) or "〈証拠なし〉"

    # ❷ プロンプトに証拠を埋め込む
    sys_msg = {
        "role": "system",
        "content": (
            "あなたは証拠付きファクトチェッカーです。"
            "必ず証拠のみを根拠に SUPPORTED / REFUTED / NOT SURE のいずれかで判定し、"
            "理由は30字以内で述べてください。"
        ),
    }
    user_msg = {
        "role": "user",
        "content": f"## 主張\n{claim}\n\n## 証拠\n{evidence_txt}",
    }
    return await openai_chat([sys_msg, user_msg], model="gpt-4o")


# ---------------------------------------------------------------------------
# CORE DRIVER (async)
# ---------------------------------------------------------------------------

async def verify_claims(claims: List[str]) -> List[Dict]:
    tasks = []
    for c in claims:
        tasks.append(_process_single_claim(c))
    return await asyncio.gather(*tasks)


async def _process_single_claim(claim: str) -> Dict:
    sources = await google_search(claim)
    verdict = await evidence_based_verdict(claim, sources)
    return {
        "claim": claim,
        "verdict": verdict,
        "sources": sources,
    }