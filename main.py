import re
import json
import requests
from flask import Flask, request
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = 12345678  # আপনার API ID
API_HASH = "your_api_hash"
BOT_TOKEN = "your_bot_token"

app = Flask(__name__)
bot = Client("bypass_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ✅ whitelist ও শর্টনার মেথড
SHORTNER_METHODS = {
    "droplink.co": "droplink",
    "indiaearnx.com": "indiaearnx"
}

# ✅ বাইপাস ফাংশনগুলো
def bypass_droplink(url):
    try:
        res = requests.get(url, allow_redirects=True, timeout=10)
        return res.url
    except:
        return None

def bypass_indiaearnx(url):
    try:
        res = requests.get(url, allow_redirects=True, timeout=10)
        return res.url
    except:
        return None

def fallback_bypass(url):
    try:
        res = requests.get(url, allow_redirects=True, timeout=10)
        return res.url
    except:
        return None

# ✅ শর্টনার অনুযায়ী ফাংশন কল
def bypass_link(url):
    for domain, method in SHORTNER_METHODS.items():
        if domain in url:
            if method == "droplink":
                return bypass_droplink(url)
            elif method == "indiaearnx":
                return bypass_indiaearnx(url)
    # fallback
    return fallback_bypass(url)

# ✅ whitelist যুক্ত করার কমান্ড
@bot.on_message(filters.command("addshortner") & filters.private)
async def add_shortner_handler(client, message: Message):
    try:
        cmd = message.text.split()
        if len(cmd) != 3:
            return await message.reply("⚠️ সঠিক ফর্ম্যাট:\n`/addshortner domain.com method`", quote=True)

        domain, method = cmd[1], cmd[2]
        SHORTNER_METHODS[domain] = method
        await message.reply(f"✅ `{domain}` শর্টনার `{method}` মেথডে যুক্ত করা হয়েছে!")
    except Exception as e:
        await message.reply(f"❌ ত্রুটি: {e}")

# ✅ লিংক মেসেজ ধরার হ্যান্ডলার
@bot.on_message(filters.text & ~filters.command("addshortner"))
async def link_handler(client, message: Message):
    urls = re.findall(r'(https?://[^\s]+)', message.text)
    if not urls:
        return

    for url in urls:
        await message.reply("🔄 লিংক বাইপাস করা হচ্ছে...", quote=True)
        final = bypass_link(url)
        if final and final != url:
            await message.reply(f"✅ মূল লিংক:\n{final}", quote=True)
        else:
            await message.reply("❌ দুঃখিত, বাইপাস করা যায়নি।", quote=True)

# ✅ Flask route (optional deploy for webhook)
@app.route("/")
def home():
    return "Bypass Bot is Alive!"

if __name__ == "__main__":
    import threading
    threading.Thread(target=lambda: bot.run()).start()
    app.run(host="0.0.0.0", port=5000)
