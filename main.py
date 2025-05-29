import re
import json
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from pyrogram import Client, filters
from pyrogram.types import Message

# ========== CONFIGURATION ==========
API_ID = 12345678  # আপনার API_ID
API_HASH = "your_api_hash"
BOT_TOKEN = "your_bot_token"
WHITELIST_FILE = "whitelist.json"
ADMIN_IDS = [123456789]  # আপনার Telegram user ID
# ===================================

app = Client("shortner_bypass_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ========== UTILITIES ==========

def load_whitelist():
    if not os.path.exists(WHITELIST_FILE):
        with open(WHITELIST_FILE, "w") as f:
            json.dump({}, f)
    with open(WHITELIST_FILE, "r") as f:
        return json.load(f)

def save_whitelist(data):
    with open(WHITELIST_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ========== BYPASS FUNCTION ==========

def bypass_link(url: str) -> str:
    whitelist = load_whitelist()
    parsed = urlparse(url)
    domain = parsed.netloc.lower().replace("www.", "")

    method = whitelist.get(domain)
    if not method:
        return None

    print(f"[Bypass] Domain: {domain} | Method: {method}")

    try:
        if method == "simple_redirect":
            resp = requests.get(url, timeout=5, allow_redirects=True)
            return resp.url

        elif method == "droplink":
            headers = {
                "User-Agent": "Mozilla/5.0"
            }
            session = requests.Session()
            resp = session.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")

            final_link = None
            for a in soup.find_all("a", href=True):
                if "redirect" in a["href"]:
                    final_link = a["href"]
                    break

            if final_link and not final_link.startswith("http"):
                final_link = "https://droplink.co" + final_link

            if final_link:
                final_resp = session.get(final_link, headers=headers, timeout=10, allow_redirects=True)
                return final_resp.url

        # ভবিষ্যতে আরও মেথড যুক্ত করতে পারবেন
    except Exception as e:
        print("[Bypass Error]", e)
        return None

# ========== COMMANDS ==========

@app.on_message(filters.command("start"))
async def start_handler(client, message: Message):
    await message.reply("👋 হ্যালো! শর্টলিংক পাঠান, আমি অরিজিনাল লিংক বের করে দেবো।")

@app.on_message(filters.command("addshortner") & filters.user(ADMIN_IDS))
async def add_shortner(client, message: Message):
    try:
        parts = message.text.split()
        if len(parts) != 3:
            return await message.reply("⚠️ সঠিক ফর্ম্যাট:\n`/addshortner domain.com method`")

        domain, method = parts[1], parts[2]
        whitelist = load_whitelist()
        whitelist[domain.lower()] = method
        save_whitelist(whitelist)
        await message.reply(f"✅ `{domain}` whitelist-এ `{method}` মেথড সহ যুক্ত হয়েছে।")
    except Exception as e:
        print("[Add Shortner Error]", e)
        await message.reply("❌ অ্যাড করতে সমস্যা হয়েছে।")

@app.on_message(filters.command("showshortners") & filters.user(ADMIN_IDS))
async def show_whitelist(client, message: Message):
    data = load_whitelist()
    if not data:
        await message.reply("⚠️ এখনো কোনো শর্টনার অ্যাড করা হয়নি।")
    else:
        text = "**🔗 Whitelisted Domains:**\n"
        for domain, method in data.items():
            text += f"• `{domain}` ➜ `{method}`\n"
        await message.reply(text)

# ========== MAIN LOGIC ==========

@app.on_message(filters.text & ~filters.command(["start", "addshortner", "showshortners"]))
async def bypass_message(client, message: Message):
    urls = re.findall(r'https?://\S+', message.text)
    if not urls:
        return

    replies = []
    for url in urls:
        original = bypass_link(url)
        if original:
            replies.append(f"🔗 <b>Bypassed:</b>\n<code>{original}</code>")
        else:
            replies.append(f"❌ <b>Could not bypass:</b> {url}")

    await message.reply("\n\n".join(replies), quote=True, parse_mode="html")

# ========== RUN ==========

if __name__ == "__main__":
    print("✅ Bot is running...")
    app.run()
