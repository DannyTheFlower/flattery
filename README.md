Чтобы всё заработало, нужно запустить файлы в следующей последовательности:
1) scraping.py — создание базы данных с актуальными ссылками Циана и фотографиями для каждой квартиры
2) model.py — создание таблицы в базе данных с результатами извлечения признаков из каждой фотографии
3) bot.py — запуск бота (предварительно в config.ini записать токен, полученный через BotFather)
