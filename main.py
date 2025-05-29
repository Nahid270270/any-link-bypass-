# main.py

import os
import json
import requests
from urllib.parse import urlparse

from flask import Flask
from threading import Thread

from pyrogram import Client, filters
from pyrogram.types import Message

# -----------------------------
# 🔧 CONFIGURATION
# -----------------------------
API_ID = int(os.getenv("API_ID", "123456"))
API_HASH = os.getenv("API_HASH", "your_api_hash")
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token")
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789"))

WHITELIST_FILE = "shortners.json"

# -----------------------------
# 🔄 WHITELIST MANAGEMENT
# -----------------------------
def load_whitelist():
    if not os.path.exists(WHITELIST_FILE):
        with open(WHITELIST_FILE, "w") as f:
            json.dump({}, f)
    with open(WHITELIST_FILE, "r") as f:
        return json.load(f)

def save_whitelist(data):
    with open(WHITELIST_FILE, "w") as f:
        json.dump(data, f, indent=2)

def is_allowed(url):
    domain = urlparse(url).netloc.replace("www.", "")
    return domain in load_whitelist()

def get_method(domain):
    return load_whitelist().get(domain)

def get_domain_key(url):
    return urlparse(url).netloc.replace("www.", "")

# -----------------------------
# 🔗 BYPASS LOGIC
# -----------------------------
def bypass_link(url):
    domain = get_domain_key(url)
    method = get_method(domain)

    if method == "simple_redirect":
        try:
            res = requests.head(url, allow_redirects=True, timeout=10)
            return res.url
        except:
            return None
    elif method == "gplink":
        return "https://example.com/final_link_from_gplinks"
    elif method == "droplink":
        return "https://example.com/final_link_from_droplink"
    else:
        return None

# -----------------------------
# 🌐 FLASK APP
# -----------------------------
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "✅ Telegram Bypass Bot is running!"

def run_flask():
    flask_app.run(host="0.0.0.0", port=8000)

# -----------------------------
# 🤖 TELEGRAM BOT
# -----------------------------
bot = Client("bypass-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.private & filters.text)
async def handle_message(client, message: Message):
    text = message.text.strip()

    if text.startswith("/addshortner"):
        if message.from_user.id != ADMIN_ID:
            return await message.reply("❌ অনুমতি নেই।")
        try:
            _, domain, method = text.split()
            whitelist = load_whitelist()
            whitelist[domain] = method
            save_whitelist(whitelist)
            return await message.reply(f"✅ `{domain}` যুক্ত করা হয়েছে `{method}` মেথডে।")
        except:
            return await message.reply("⚠️ সঠিক ফর্ম্যাট:\n`/addshortner domain.com method`")

    elif text.startswith("/removeshortner"):
        if message.from_user.id != ADMIN_ID:
            return await message.reply("❌ অনুমতি নেই।")
        try:
            _, domain = text.split()
            whitelist = load_whitelist()
            if domain in whitelist:
                del whitelist[domain]
                save_whitelist(whitelist)
                return await message.reply(f"❌ `{domain}` মুছে ফেলা হয়েছে।")
            else:
                return await message.reply("⚠️ এই ডোমেইন whitelist-এ নেই।")
        except:
            return await message.reply("⚠️ সঠিক ফর্ম্যাট:\n`/removeshortner domain.com`")

    elif text.startswith("/showshortners"):
        if message.from_user.id != ADMIN_ID:
            return await message.reply("❌ অনুমতি নেই।")
        whitelist = load_whitelist()
        if not whitelist:
            return await message.reply("⚠️ এখনো কোনো শর্টনার এড করা হয়নি।")
        msg = "**📋 whitelist শর্টনার তালিকা:**\n"
        for k, v in whitelist.items():
            msg += f"- `{k}` → `{v}`\n"
        return await message.reply(msg)

    elif text.startswith("/start"):
        return await message.reply("👋 হ্যালো! আমাকে শর্টলিংক পাঠান এবং আমি বাইপাস করে মূল লিংক বের করে দিব।")

    elif text.startswith("http"):
        url = text
        if not is_allowed(url):
            return await message.reply("❌ এই লিংকটি whitelist-এ নেই।\n\n📌 এড করতে: `/addshortner domain method`")
        await message.reply("🔄 লিংক বাইপাস করা হচ্ছে...")
        result = bypass_link(url)
        if result:
            await message.reply(f"✅ মূল লিংক:\n{result}")
        else:
            await message.reply("❌ দুঃখিত, বাইপাস করা যায়নি।")
    else:
        await message.reply("⚠️ একটি বৈধ শর্টলিংক পাঠান অথবা কমান্ড ব্যবহার করুন।")

# -----------------------------
# 🚀 START
# -----------------------------
if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.run()
