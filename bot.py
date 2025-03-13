import yt_dlp
import requests
import json
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from threading import Thread
import asyncio
import nest_asyncio
import os
from dotenv import load_dotenv
import logging

# Apply nest_asyncio to avoid event loop conflict
nest_asyncio.apply()

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
GOFILE_FOLDER_ID = "gvcT2t"
GOFILE_ACCOUNT_TOKEN = os.getenv("GOFILE_ACCOUNT_TOKEN")
CHANNEL_USERNAME = "@TOOLS_BOTS_KING"
COOKIES_FILE_PATH = "cookies.txt"  # Path to save cookies

# Initialize Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "YouTube to MP3 Bot is Running!"

bot = Bot(token=BOT_TOKEN)

# **Load Cookies from Environment Variable**
cookies_data = os.getenv("COOKIES_DATA", "")
if cookies_data:
    with open(COOKIES_FILE_PATH, "w") as file:
        file.write(cookies_data)
    print("✅ Cookies file created successfully!")
else:
    print("⚠️ No cookies found in environment variables!")

# Subscription check
async def is_user_subscribed(user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"Subscription check failed: {e}")
        return False

async def force_join(update: Update):
    await update.message.reply_text(
        f"🚨 Join our channel to use this bot! \n➡️ [Join Now](https://t.me/{CHANNEL_USERNAME[1:]})",
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

async def start(update: Update, context):
    user_id = update.message.chat_id
    if not await is_user_subscribed(user_id):
        await force_join(update)
        return
    await update.message.reply_text("🎵 Send a YouTube link to download music in MP3 format!")

def download_music(url, save_path):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{save_path}/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'cookiefile': COOKIES_FILE_PATH  # Use the cookies file
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
            return os.path.join(save_path, f"{info['title']}.mp3")
        except yt_dlp.utils.DownloadError as e:
            print(f"Download failed: {e}")
            return None

def upload_to_gofile(file_path):
    url = "https://api.gofile.io/uploadFile"
    try:
        with open(file_path, 'rb') as file:
            response = requests.post(url, files={"file": file}, data={"token": GOFILE_ACCOUNT_TOKEN, "folderId": GOFILE_FOLDER_ID})
        response.raise_for_status()
        return response.json().get("data", {}).get("downloadPage", "Upload failed")
    except Exception as e:
        print(f"Upload failed: {e}")
        return "Upload failed"

async def handle_message(update: Update, context):
    user_id = update.message.chat_id
    if not await is_user_subscribed(user_id):
        await force_join(update)
        return
    
    url = update.message.text.strip()
    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("❌ Invalid YouTube URL!")
        return
    
    save_path = os.getcwd()
    await update.message.reply_text("⏳ Downloading music...")
    mp3_path = download_music(url, save_path)
    
    if mp3_path:
        await update.message.reply_text("⬆️ Uploading to GoFile...")
        gofile_link = upload_to_gofile(mp3_path)
        await update.message.reply_text(f"✅ Music uploaded: {gofile_link}")
        os.remove(mp3_path)
    else:
        await update.message.reply_text("❌ Failed to download the music. Please try again later.")

def run_flask():
    PORT = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=PORT)

def run_bot():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(application.run_polling())

if __name__ == "__main__":
    # Run Flask in a separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.start()
    
    # Run Telegram bot
    run_bot()
