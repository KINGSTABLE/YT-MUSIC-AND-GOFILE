import os
import yt_dlp
import requests
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import CommandHandler, CallbackContext, Updater
from tqdm import tqdm

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
GOFILE_FOLDER_ID = "gvcT2t"
GOFILE_ACCOUNT_TOKEN = os.getenv("GOFILE_ACCOUNT_TOKEN")
CHANNEL_USERNAME = "@TOOLS_BOTS_KING"

# Initialize Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "YouTube to MP3 Bot is Running!"

bot = Bot(token=BOT_TOKEN)

# Subscription check
def is_user_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"Subscription check failed: {e}")
        return False

def force_join(update: Update):
    update.message.reply_text(
        f"🚨 Join our channel to use this bot! \n➡️ [Join Now](https://t.me/{CHANNEL_USERNAME[1:]})",
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

def start(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    if not is_user_subscribed(user_id):
        force_join(update)
        return
    update.message.reply_text("🎵 Send a YouTube link to download music in MP3 format!")

def download_music(url, save_path):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return os.path.join(save_path, f"{info['title']}.mp3")

def upload_to_gofile(file_path):
    url = "https://api.gofile.io/uploadFile"
    with open(file_path, 'rb') as file:
        response = requests.post(url, files={"file": file}, data={"token": GOFILE_ACCOUNT_TOKEN, "folderId": GOFILE_FOLDER_ID})
    return response.json().get("data", {}).get("downloadPage", "Upload failed")

def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    if not is_user_subscribed(user_id):
        force_join(update)
        return
    
    url = update.message.text.strip()
    if "youtube.com" not in url and "youtu.be" not in url:
        update.message.reply_text("❌ Invalid YouTube URL!")
        return
    
    save_path = os.getcwd()
    update.message.reply_text("⏳ Downloading music...")
    mp3_path = download_music(url, save_path)
    
    update.message.reply_text("⬆️ Uploading to GoFile...")
    gofile_link = upload_to_gofile(mp3_path)
    update.message.reply_text(f"✅ Music uploaded: {gofile_link}")
    os.remove(mp3_path)

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("download", handle_message))
    updater.start_polling()
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    main()
