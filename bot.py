import telebot
import configparser
import sqlite3
import numpy as np
from keras.utils.image_utils import img_to_array
from model import find_similar_images
from PIL import Image

config = configparser.ConfigParser()
config.read('config.ini')

TOKEN = config['Bot']['token']

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Загрузи изображение квартиры, и я попробую найти подходящую квартиру в базе данных.")


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open('user_photo.jpg', 'wb') as new_file:
        new_file.write(downloaded_file)
    bot.reply_to(message, "Фото получено! Обрабатываю...")

    img = Image.open('user_photo.jpg')
    img_array = img_to_array(img)
    similar_images = find_similar_images(img_array)

    conn = sqlite3.connect('rentals.db')
    cur = conn.cursor()

    for img_id in similar_images:
        cur.execute("SELECT photo, link FROM rentals WHERE id=?", (img_id,))
        photo_data, link = cur.fetchone()
        bot.send_message(message.chat.id, f"Ссылка: {link}")
        with open('temp.jpg', 'wb') as img_file:
            img_file.write(photo_data)
        with open('temp.jpg', 'rb') as img_file:
            bot.send_photo(message.chat.id, img_file)

    conn.close()


bot.polling()
