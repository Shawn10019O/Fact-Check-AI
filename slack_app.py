from fastapi import FastAPI, Request
from slack_bolt.adapter.fastapi import SlackRequestHandler
from slack_bolt.async_app import AsyncApp
from slack_sdk.web.async_client import AsyncWebClient
from dotenv import load_dotenv
from pyngrok import ngrok 
import os, tempfile, aiohttp, asyncio
import atexit

load_dotenv()  # .env 読み込み

# ------------ ngrok 起動 -------------
ngrok.set_auth_token(os.getenv("NGROK_AUTH_TOKEN"))
public_url = ngrok.connect(8000, bind_tls=True)   # http://→https://
print(f" 🌐  Public URL: {public_url}")

atexit.register(lambda: ngrok.disconnect(public_url))

# --- Bolt 初期化 -----------------------------------------------------------
bolt_app = AsyncApp(
    token=os.environ["SLACK_BOT_TOKEN"],
    signing_secret=os.environ["SLACK_SIGNING_SECRET"],
)
handler = SlackRequestHandler(bolt_app)

# --- あなたの既存パイプライン ---------------------------------------------
from demo3 import read_document, sanitize_text, bullets_to_sentences, extract_claims, verify_claims
# ↑ 上で貼り付けたコードを `factcheck_core.py` 等にそのまま分離しておくとスマート

# --- ファイル共有イベント --------------------------------------------------
@bolt_app.event("file_shared")
async def on_file_shared(body, client: AsyncWebClient, logger):
    file_id  = body["event"]["file_id"]
    info     = await client.files_info(file=file_id)
    url      = info["file"]["url_private_download"]
    filename = info["file"]["name"]

    headers = {"Authorization": f"Bearer {os.environ['SLACK_BOT_TOKEN']}"}
    async with aiohttp.ClientSession() as sess, sess.get(url, headers=headers) as resp:
        data = await resp.read()
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1])
    tmp.write(data); tmp.close()

    text, err = read_document(tmp.name)
    if err:
        await client.chat_postMessage(channel=body["event"]["channel_id"], text=f"❌ {err}")
        return

    bullets    = sanitize_text(text).split("\n")
    sentences  = await bullets_to_sentences(bullets)
    claims     = await extract_claims("\n".join(sentences))
    results    = await verify_claims(claims)
    refuted    = [r for r in results if r["verdict"].startswith("REFUTED")]

    if not refuted:
        msg = "✅ 誤りのある主張は見つかりませんでした！"
    else:
        msg = "*REFUTED claims:*\n" + "\n".join(f"• {r['claim']}" for r in refuted)
    await client.chat_postMessage(channel=body["event"]["channel_id"], text=msg)

# --- FastAPI エンドポイント -----------------------------------------------
app = FastAPI()
@app.post("/slack/events")
async def slack_events(request: Request):
    return await handler.handle(request)

