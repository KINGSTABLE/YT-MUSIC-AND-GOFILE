import os
import requests
import telebot
from pytube import YouTube, request
from telebot import types
from flask import Flask, request as flask_request

API_TOKEN = ''
LOG_CHANNEL_ID = -
CHANNEL_USERNAME = ""
WEBHOOK_URL = ''  # Replace with your webhook URL

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

def load_cookies(file_path):
    cookies = {}
    with open(file_path, "r") as file:
        for line in file:
            if not line.startswith("#"):
                parts = line.strip().split("\t")
                if len(parts) == 7:
                    domain, host_only, path, secure, expiration, name, value = parts
                    cookies[name] = value
    return cookies

def set_cookies(cookies):
    cookie_str = '; '.join([f'{name}={value}' for name, value in cookies.items()])
    request.default_cookies = cookie_str

def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        return False

def download_youtube_video(url, cookies):
    set_cookies(cookies)  # Set cookies before creating YouTube object
    yt = YouTube(url)
    stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    file_path = stream.download()
    return file_path

def upload_to_gofile(file_path):
    with open(file_path, 'rb') as file:
        response = requests.post('https://api.gofile.io/uploadFile', files={'file': file})
        response_data = response.json()
        return response_data['data']['downloadPage']

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if check_subscription(user_id):
        bot.send_message(message.chat.id, "You are already subscribed to the channel.")
    else:
        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton("Subscribe", url=f"https://t.me/{CHANNEL_USERNAME}")
        markup.add(button)
        bot.send_message(message.chat.id, "Please subscribe to our channel first.", reply_markup=markup)

@bot.message_handler(commands=['download'])
def download(message):
    user_id = message.from_user.id
    if check_subscription(user_id):
        msg = bot.send_message(message.chat.id, "Please send the YouTube video URL.")
        bot.register_next_step_handler(msg, request_cookies)
    else:
        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton("Subscribe", url=f"https://t.me/{CHANNEL_USERNAME}")
        markup.add(button)
        bot.send_message(message.chat.id, "You need to subscribe to our channel first.", reply_markup=markup)

def request_cookies(message):
    url = message.text
    msg = bot.send_message(message.chat.id, "Please upload your cookies.txt file.")
    bot.register_next_step_handler(msg, process_download, url)

def process_download(message, url):
    if message.document:
        # Download the cookies.txt file
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        file_path = os.path.join("cookies", message.document.file_name)
        
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        
        cookies = load_cookies(file_path)
        
        bot.send_message(message.chat.id, "Downloading video, please wait...")
        try:
            file_path = download_youtube_video(url, cookies)
        except Exception as e:
            bot.send_message(message.chat.id, f"Error downloading video: {e}")
            os.remove(file_path)
            return
        
        bot.send_message(message.chat.id, "Uploading video to Gofile, please wait...")
        try:
            download_link = upload_to_gofile(file_path)
        except Exception as e:
            bot.send_message(message.chat.id, f"Error uploading video: {e}")
            os.remove(file_path)
            return
        
        bot.send_message(message.chat.id, f"Here is your download link: {download_link}")
        
        log_message = f"New video download request:\nUser ID: {message.from_user.id}\nUsername: @{message.from_user.username}\nDownload Link: {download_link}"
        bot.send_message(LOG_CHANNEL_ID, log_message)
        
        os.remove(file_path)  # Remove the downloaded video file
        os.remove("cookies/" + message.document.file_name)  # Remove the cookies file

@app.route('/' + API_TOKEN, methods=['POST'])
def webhook():
    json_str = flask_request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '!', 200

@app.route('/')
def index():
    return 'Hello, this is the bot webhook endpoint.', 200

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL + API_TOKEN)
    if not os.path.exists("cookies"):
        os.makedirs("cookies")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
