import telebot
from telebot import types
import configparser
import sqlite3
from keras.utils.image_utils import img_to_array
from model import find_similar_images
from messages import *
from PIL import Image
from datetime import datetime

config = configparser.ConfigParser()
config.read('config.ini')

TOKEN = config['Bot']['token']

bot = telebot.TeleBot(TOKEN)


def logging_message(user_id, user_name, message):
    text = f"{datetime.now()} - {user_id} - {user_name} - {message}"
    print(text)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    logging_message(call.from_user.id, call.from_user.username, call.data)
    chat_id, username, data = call.from_user.id, call.from_user.username, call.data
    if 'flats_' in data:
        flats = data.split('_')[1].split(';')
        index = int(data.split('_')[2])
        send_flats(chat_id, flats, index, call.message.id)


def send_main_keyboard(chat_id, text):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(SEARCH_BUTTON))
    markup.add(types.KeyboardButton(INFO_BUTTON))
    bot.send_message(chat_id, text, parse_mode='HTML', reply_markup=markup)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    send_main_keyboard(message.chat.id, START_MESSAGE)


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open('user_photo.jpg', 'wb') as new_file:
        new_file.write(downloaded_file)
    send_main_keyboard(message.chat.id, PHOTO_UPLOADED)

    img = Image.open('user_photo.jpg')
    img_array = img_to_array(img)
    similar_images = find_similar_images(img_array)

    send_main_keyboard(message.chat.id, FLAT_FOUNDED)
    send_flats(message.chat.id, similar_images, 0)


def send_flats(chat_id, flats, index, msg_id=None):
    conn = sqlite3.connect('rentals.db')
    cur = conn.cursor()
    flat_id = flats[index]
    cur.execute("SELECT * FROM rentals WHERE id=?", (flat_id,))
    data = cur.fetchone()
    msg = FLAT_TEXT
    msg = msg.replace("{ID}", str(data[0]))
    msg = msg.replace("{METRO}", str(data[2]))
    msg = msg.replace("{SIZE}", str(data[3]))
    msg = msg.replace("{URL}", str(data[1]))
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(GO_LINK_BUTTON, data[1]))
    buttons = []
    if index != 0:
        buttons.append(types.InlineKeyboardButton(LEFT, callback_data=f"flats_{';'.join([str(flat) for flat in flats])}_{index - 1}"))
    if index != len(flats) - 1:
        buttons.append(types.InlineKeyboardButton(RIGHT, callback_data=f"flats_{';'.join([str(flat) for flat in flats])}_{index + 1}"))
    markup.add(*buttons)
    with open('temp.jpg', 'wb') as img_file:
        img_file.write(data[4])
    if msg_id is None:
        bot.send_photo(chat_id, open('temp.jpg', 'rb'), caption=msg, parse_mode='HTML', reply_markup=markup)
    else:
        bot.edit_message_media(types.InputMediaPhoto(open('temp.jpg', 'rb'), caption=msg, parse_mode='HTML'),
                               chat_id, msg_id, reply_markup=markup)


@bot.message_handler(func=lambda message: True)
def message_handler(message):
    logging_message(message.chat.id, message.from_user.username, message.text)
    chat_id, username, text = message.chat.id, message.from_user.username, message.text
    if text == SEARCH_BUTTON:
        bot.send_message(chat_id, SEARCH_TEXT, parse_mode="HTML")
    elif text == INFO_BUTTON:
        bot.send_message(chat_id, INFO_TEXT, parse_mode="HTML")
    else:
        bot.send_message(chat_id, TEXT_NOT_RECOGNIZED, parse_mode="HTML")


bot.polling()
