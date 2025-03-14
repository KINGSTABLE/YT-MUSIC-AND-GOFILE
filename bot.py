import os
import requests
import telebot
from pytube import YouTube, request
from telebot import types
from flask import Flask, request as flask_request

API_TOKEN = '7809747739:AAEwNmouf6LZQwtNjOXL5Ms4VptLb634Eic'
LOG_CHANNEL_ID = -1002661069692
CHANNEL_USERNAME = "@TOOLS_BOTS_KING"
WEBHOOK_URL = 'https://dusty-willa-billagh-0b310326.koyeb.app/'  # Replace with your webhook URL

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

def write_cookies_to_file(cookies):
    with open("cookies.txt", "w") as file:
        for cookie in cookies:
            file.write(f"{cookie['domain']}\t{'TRUE' if not cookie['hostOnly'] else 'FALSE'}\t{cookie['path']}\t{'TRUE' if cookie['secure'] else 'FALSE'}\t{int(cookie['expirationDate']) if 'expirationDate' in cookie else '0'}\t{cookie['name']}\t{cookie['value']}\n")

cookies = [
    {"domain": ".youtube.com", "expirationDate": 1775818772.593637, "hostOnly": False, "httpOnly": False, "name": "__Secure-1PAPISID", "path": "/", "sameSite": "unspecified", "secure": True, "session": False, "storeId": "0", "value": "cxcsjVza10XKXpS9/A_mEvxtbtXYvr7NBK", "id": 1},
    {"domain": ".youtube.com", "expirationDate": 1775818772.594913, "hostOnly": False, "httpOnly": True, "name": "__Secure-1PSID", "path": "/", "sameSite": "unspecified", "secure": True, "session": False, "storeId": "0", "value": "g.a000uQiZNwbi_CXaiKKOXmqbCiJ7uVRFeAAbkZwhZhMwrJJhq30A2VDuRBXEl3dBDTQbsFf5rgACgYKATkSARASFQHGX2Mi728K0k8AE9STSjPQJy83QhoVAUF8yKq8_n12IYs4t54BFIafDsVL0076", "id": 2},
    {"domain": ".youtube.com", "expirationDate": 1773515113.406936, "hostOnly": False, "httpOnly": True, "name": "__Secure-1PSIDCC", "path": "/", "sameSite": "unspecified", "secure": True, "session": False, "storeId": "0", "value": "AKEyXzW8DUB15VjS-teKjr4Px1NaUPv3ywsrlpbkhHd_whdpW3hKKdNpQJZzsGzTjnxWe_pLONs", "id": 3},
    {"domain": ".youtube.com", "expirationDate": 1773514570.878119, "hostOnly": False, "httpOnly": True, "name": "__Secure-1PSIDTS", "path": "/", "sameSite": "unspecified", "secure": True, "session": False, "storeId": "0", "value": "sidts-CjIB7pHptdPfxee_a3VBK7LUopyoMTJC-iYyM-VbLl7czOweMe3i_106SGVWTK3YjxdP8BAA", "id": 4},
    {"domain": ".youtube.com", "expirationDate": 1775818772.593669, "hostOnly": False, "httpOnly": False, "name": "__Secure-3PAPISID", "path": "/", "sameSite": "no_restriction", "secure": True, "session": False, "storeId": "0", "value": "cxcsjVza10XKXpS9/A_mEvxtbtXYvr7NBK", "id": 5},
    {"domain": ".youtube.com", "expirationDate": 1775818772.594972, "hostOnly": False, "httpOnly": True, "name": "__Secure-3PSID", "path": "/", "sameSite": "no_restriction", "secure": True, "session": False, "storeId": "0", "value": "g.a000uQiZNwbi_CXaiKKOXmqbCiJ7uVRFeAAbkZwhZhMwrJJhq30AWtCAV7wnz41GcGTEs6VYjQACgYKAUESARASFQHGX2MiVwRyTGU2HlJyVq0DJrYtgBoVAUF8yKoBi29yE7tr_S_XIv8XVxSK0076", "id": 6},
    {"domain": ".youtube.com", "expirationDate": 1773515113.406999, "hostOnly": False, "httpOnly": True, "name": "__Secure-3PSIDCC", "path": "/", "sameSite": "no_restriction", "secure": True, "session": False, "storeId": "0", "value": "AKEyXzWYPICe2UnivVfnkRJMuLY2-zXwPkKfmHcPRkcIWpDRFmi9hRqzF5SvbGTLV-3BeB0saTly", "id": 7},
    {"domain": ".youtube.com", "expirationDate": 1773514570.878339, "hostOnly": False, "httpOnly": True, "name": "__Secure-3PSIDTS", "path": "/", "sameSite": "no_restriction", "secure": True, "session": False, "storeId": "0", "value": "sidts-CjIB7pHptdPfxee_a3VBK7LUopyoMTJC-iYyM-VbLl7czOweMe3i_106SGVWTK3YjxdP8BAA", "id": 8},
    {"domain": ".youtube.com", "expirationDate": 1775818772.593575, "hostOnly": False, "httpOnly": False, "name": "APISID", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "nBKpgI_m9LBlGGrZ/AipbVsQfvdInVX4KP", "id": 9},
    {"domain": ".youtube.com", "expirationDate": 1775818772.592879, "hostOnly": False, "httpOnly": True, "name": "HSID", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "A_lMsxLjV21eD22mn", "id": 10},
    {"domain": ".youtube.com", "expirationDate": 1776094606.901127, "hostOnly": False, "httpOnly": True, "name": "LOGIN_INFO", "path": "/", "sameSite": "no_restriction", "secure": True, "session": False, "storeId": "0", "value": "AFmmF2swRAIgWrOPhV7BXfF8dOWUa1m9O9H5tn23J4gvmgGy6g9eaQkCIC80REDM3zaG7CtP-jsYLzVj8MJjPiwSqXzbNgX9HZ56:QUQ3MjNmeWNKTVNTUjFBRWZDN1QxTHhnN2NCdG5WRnFpVFVjbWNWZ3B3VWVVc0d6dlBfT1FHeFlGeGRIUlRNRjZHbV9HdWV6S1pFNE9ZOFc0cUlDVGpKUlB6MmluWWhaU0xPcFlWV3AyZllUcFJHTnVuMVk0ZG9KX1IyaWxTWUp3QklTYUhUYmFDUUY5bGxwN2ZmeTFfek9HWDJtWklQWnZB", "id": 11},
    {"domain": ".youtube.com", "expirationDate": 1751400209.879365, "hostOnly": False, "httpOnly": True, "name": "NID", "path": "/", "sameSite": "unspecified", "secure": True, "session": False, "storeId": "0", "value": "520=Q3H2MtkBXKy1JhKR8LqLnRn1p_rR50Lv6De2c7G4bX2OLhgYBN_vqx3s4zXPLyWcRF31gUuQt9u6C-kVCJlZfsboVKBnBAUOsac4JT1K_Bj4G7FNkP_DBqFRjFKlWL90PRRZvJaS5a34eWGJ51GKA7-tSN7UH1-F3xhgnL5u9WnhMIv07vi0y_wtG6Toi7LbSZWyDlJFtU5Yf7j4SVEgthpB8QJi-v_NIP0DyA-Z0YP8_TOPxToIa0RmWsH8AZJdIF9-Jf3dS7A4B3U", "id": 12},
    {"domain": ".youtube.com", "expirationDate": 1776538566.066077, "hostOnly": False, "httpOnly": False, "name": "PREF", "path": "/", "sameSite": "unspecified", "secure": True, "session": False, "storeId": "0", "value": "f4=4000000&tz=Asia.Calcutta&f6=40000400&f5=30000&f7=150", "id": 13},
    {"domain": ".youtube.com", "expirationDate": 1775818772.593608, "hostOnly": False, "httpOnly": False, "name": "SAPISID", "path": "/", "sameSite": "unspecified", "secure": True, "session": False, "storeId": "0", "value": "cxcsjVza10XKXpS9/A_mEvxtbtXYvr7NBK", "id": 14},
    {"domain": ".youtube.com", "expirationDate": 1775818772.594791, "hostOnly": False, "httpOnly": False, "name": "SID", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "g.a000uQiZNwbi_CXaiKKOXmqbCiJ7uVRFeAAbkZwhZhMwrJJhq30AMcD715l2J64dgstBqDGgzwACgYKAboSARASFQHGX2MiF8dxoo-Kcjwc8mGHd2hh4hoVAUF8yKqCF55Ws6ITem2nAp9FFpzS0076", "id": 15},
    {"domain": ".youtube.com", "expirationDate": 1773515113.406761, "hostOnly": False, "httpOnly": False, "name": "SIDCC", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "AKEyXzUlmwVIXKIoIWbL1RWH2d1gcKN28QO2v3Y8MZ83QJknSQmu8yKDYbPzhimlLr4G3vQKtUg", "id": 16},
    {"domain": ".youtube.com", "expirationDate": 1775818772.593476, "hostOnly": False, "httpOnly": True, "name": "SSID", "path": "/", "sameSite": "unspecified", "secure": True, "session": False, "storeId": "0", "value": "Aj89XVRSavdq-_97I", "id": 17}
]

write_cookies_to_file(cookies)

# Load cookies from a file
def load_cookies():
    cookies = {}
    try:
        with open("cookies.txt", "r") as file:
            for line in file:
                if not line.startswith("#"):
                    parts = line.strip().split("\t")
                    if len(parts) == 7:
                        domain, host_only, path, secure, expiration, name, value = parts
                        cookies[name] = value
    except FileNotFoundError:
        print("Error: cookies.txt file not found.")
    return cookies

def set_cookies():
    cookies = load_cookies()
    cookie_str = '; '.join([f'{name}={value}' for name, value in cookies.items()])
    request.default_cookies = cookie_str

def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        return False

def download_youtube_video(url):
    set_cookies()  # Set cookies before creating YouTube object
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
    try:
        file_path = download_youtube_video(url)
    except Exception as e:
        bot.send_message(message.chat.id, f"Error downloading video: {e}")
        return

    bot.send_message(message.chat.id, "Uploading video to Gofile, please wait...")
    try:
        download_link = upload_to_gofile(file_path)
    except Exception as e:
        bot.send_message(message.chat.id, f"Error uploading video: {e}")
        return

    bot.send_message(message.chat.id, f"Here is your download link: {download_link}")

    log_message = f"New video download request:\nUser ID: {user_id}\nUsername: @{username}\nDownload Link: {download_link}"
    bot.send_message(LOG_CHANNEL_ID, log_message)

    os.remove(file_path)

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
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
