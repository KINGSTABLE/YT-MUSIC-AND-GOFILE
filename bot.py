import os
import requests
import telebot
from pytube import YouTube
from telebot import types

API_TOKEN = '7809747739:AAEwNmouf6LZQwtNjOXL5Ms4VptLb634Eic'
LOG_CHANNEL_ID = -1002661069692
CHANNEL_USERNAME = "@TOOLS_BOTS_KING"

bot = telebot.TeleBot(API_TOKEN)

def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        return False

def download_youtube_video(url):
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
        bot.register_next_step_handler(msg, process_url)
    else:
        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton("Subscribe", url=f"https://t.me/{CHANNEL_USERNAME}")
        markup.add(button)
        bot.send_message(message.chat.id, "You need to subscribe to our channel first.", reply_markup=markup)

def process_url(message):
    url = message.text
    user_id = message.from_user.id
    username = message.from_user.username

    bot.send_message(message.chat.id, "Downloading video, please wait...")
    file_path = download_youtube_video(url)

    bot.send_message(message.chat.id, "Uploading video to Gofile, please wait...")
    download_link = upload_to_gofile(file_path)

    bot.send_message(message.chat.id, f"Here is your download link: {download_link}")

    log_message = f"New video download request:\nUser ID: {user_id}\nUsername: @{username}\nDownload Link: {download_link}"
    bot.send_message(LOG_CHANNEL_ID, log_message)

    os.remove(file_path)

if __name__ == '__main__':
    bot.polling(none_stop=True)
