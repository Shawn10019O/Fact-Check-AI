from typing import List, Dict
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential_jitter,
    retry_if_exception_type,
)
import json
from openai import AsyncOpenAI, OpenAIError

client = AsyncOpenAI()

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential_jitter(initial=1, max=10),
    retry=retry_if_exception_type(OpenAIError),
)
async def openai_chat(messages: List[Dict], *, model: str = "gpt-4o-mini") -> str:
    rsp = await client.chat.completions.create( 
        model=model,
        messages=messages,
        temperature=0.0,
    ) # type: ignore[arg-type]
    content = rsp.choices[0].message.content or ""
    return content.strip()


BULLET_SYS = {
    "role": "system",
    "content": (
        "あなたは、スライドの断片的なテキストを、人間が読んで意味が通る文章に変換するアシスタントです。"
        "キーワード、箇条書き、見出しなどを、文脈を考慮してつなぎ合わせ、自然な日本語の文章にしてください。\n"
        "ただし、以下のルールを厳守してください：\n"
        "1. 元のテキストにない情報を絶対に追加しないこと。\n"
        "2. 可能な限り、元のテキストの単語や表現をそのまま使うこと。\n"
        "3. 元のテキストが既に完全な文章である場合は、そのまま使用すること。\n\n"
        "例：「1962年」「J.C.R. Lickliderの構想」→「1962年にJ.C.R. Lickliderが『Galactic Network』構想を提唱した。」のように、関連する断片を1つの文にまとめてください。\n"
        "結果はJSON形式 `{'sentences':[...]} ` で返してください。"
    )
}
BULLET_FUNC_SPEC = {
    "name": "return_sentences",
    "parameters": {
        "type": "object",
        "properties": {
            "sentences": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["sentences"],
    },
}

async def bullets_to_sentences(bullets: list[str]) -> list[str]:
    """`bullets` = 箇条書き1行ごとのリスト"""
    prompt = "\n".join(bullets)
    rsp = await client.chat.completions.create( # type: ignore[arg-type,call-overload]
        model="gpt-4o-mini",
        messages=[BULLET_SYS, {"role": "user", "content": prompt}],
        functions=[BULLET_FUNC_SPEC],
        function_call={"name": "return_sentences"},
        temperature=0.0,
    )
    args = rsp.choices[0].message.function_call.arguments
    return json.loads(args)["sentences"]