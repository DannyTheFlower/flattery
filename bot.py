import telebot
import configparser

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


bot.polling()
