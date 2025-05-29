import re
import json
import requests
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = 12345678  # আপনার API ID দিন
API_HASH = "your_api_hash"
BOT_TOKEN = "your_bot_token"

app = Flask(__name__)
bot = Client("bypass_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ✅ whitelist শর্টনার
SHORTNER_METHODS = {
    "droplink.co": "droplink",
    "indiaearnx.com": "indiaearnx"
}

# ✅ শর্টনার অনুযায়ী ফাংশন
def bypass_droplink(url):
    print(f"[DEBUG] Trying droplink bypass for {url}")
    try:
        res = requests.get(url, allow_redirects=True, timeout=10)
        print(f"[DEBUG] Final URL: {res.url}")
        return res.url
    except Exception as e:
        print(f"[ERROR] droplink bypass failed: {e}")
        return None

def bypass_indiaearnx(url):
    print(f"[DEBUG] Trying indiaearnx bypass for {url}")
    try:
        res = requests.get(url, allow_redirects=True, timeout=10)
        print(f"[DEBUG] Final URL: {res.url}")
        return res.url
    except Exception as e:
        print(f"[ERROR] indiaearnx bypass failed: {e}")
        return None

def fallback_bypass(url):
    print(f"[DEBUG] Trying fallback bypass for {url}")
    try:
        res = requests.get(url, allow_redirects=True, timeout=10)
        print(f"[DEBUG] Final fallback URL: {res.url}")
        return res.url
    except Exception as e:
        print(f"[ERROR] fallback bypass failed: {e}")
        return None

# ✅ মেইন বাইপাস ফাংশন
def bypass_link(url):
    print(f"[DEBUG] Processing URL: {url}")
    for domain, method in SHORTNER_METHODS.items():
        if domain in url:
            print(f"[DEBUG] Matched domain: {domain}, method: {method}")
            if method == "droplink":
                return bypass_droplink(url)
            elif method == "indiaearnx":
                return bypass_indiaearnx(url)
            else:
                print(f"[WARN] Unknown method: {method}")
                return fallback_bypass(url)
    print("[DEBUG] No matched domain, using fallback...")
    return fallback_bypass(url)

# ✅ শর্টনার whitelist যোগ করার কমান্ড
@bot.on_message(filters.command("addshortner") & filters.private)
async def add_shortner_handler(client, message: Message):
    try:
        cmd = message.text.split()
        if len(cmd) != 3:
            return await message.reply("⚠️ সঠিক ফর্ম্যাট:\n`/addshortner domain.com method`", quote=True)

        domain, method = cmd[1], cmd[2]
        SHORTNER_METHODS[domain] = method
        print(f"[DEBUG] Added shortner: {domain} -> {method}")
        await message.reply(f"✅ `{domain}` শর্টনার `{method}` মেথডে যুক্ত করা হয়েছে!")
    except Exception as e:
        await message.reply(f"❌ ত্রুটি: {e}")
        print(f"[ERROR] addshortner command failed: {e}")

# ✅ যেকোনো মেসেজ থেকে লিংক খোঁজা এবং বাইপাস করা
@bot.on_message(filters.text & ~filters.command("addshortner"))
async def link_handler(client, message: Message):
    urls = re.findall(r'(https?://[^\s]+)', message.text)
    if not urls:
        return

    for url in urls:
        await message.reply("🔄 লিংক বাইপাস করা হচ্ছে...", quote=True)
        print(f"[DEBUG] Received URL: {url}")
        final = bypass_link(url)
        if final and final != url:
            await message.reply(f"✅ মূল লিংক:\n{final}", quote=True)
        else:
            await message.reply("❌ দুঃখিত, বাইপাস করা যায়নি।", quote=True)

# ✅ Flask web route
@app.route("/")
def home():
    return "Bypass Bot is Running"

# ✅ রান করুন
if __name__ == "__main__":
    import threading
    threading.Thread(target=lambda: bot.run()).start()
    app.run(host="0.0.0.0", port=5000)
