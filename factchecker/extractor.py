from typing import List
from dotenv import load_dotenv
from openai import AsyncOpenAI
import json

load_dotenv()

client = AsyncOpenAI()

EXTRACT_SYS_MSG = {
    "role": "system",
    "content": (
        "あなたはテキスト抽出ボットです。あなたの唯一の仕事は、入力されたテキストの中から、文章として成立している部分を「原文を一字一句変更せず」にそのまま抜き出すことです。"
        "解釈、要約、言い換え、情報の追加、文章の生成は絶対に禁止します。"
        "結果は指定されたJSON形式で返してください。"
    )
}

EXTRACT_FUNC_SPEC = {
    "name": "return_claims",
    "description": "テキスト中の主張を文字列のリストで返す",
    "parameters": {
        "type": "object",
        "properties": {
            "claims": {
                "type": "array",
                "items": {"type": "string"}
            }
        },
        "required": ["claims"],
    },
}


async def extract_claims(text: str) -> List[str]:
    messages = [EXTRACT_SYS_MSG, {"role": "user", "content": text}]
    rsp = await client.chat.completions.create( # type: ignore[arg-type,call-overload]
        model="gpt-4o-mini",
        messages=messages,
        functions=[EXTRACT_FUNC_SPEC],
        function_call={"name": "return_claims"},
        temperature=0.0,
    )
    payload = rsp.choices[0].message.function_call.arguments

    claims = json.loads(payload)["claims"]
    return claims