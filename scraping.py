import requests
import sqlite3
from bs4 import BeautifulSoup


def get_card_info(card):
    soup = BeautifulSoup(str(card), 'html.parser')

    try:
        link = soup.find(class_='_93444fe79c--media--9P6wN').get('href')
        metro = soup.find(class_='_93444fe79c--container--w7txv').find_all('div')[-2].text.strip()
        price = ''.join(soup.find(class_='_93444fe79c--color_black_100--kPHhJ _93444fe79c--lineHeight_28px--whmWV '
                                         '_93444fe79c--fontWeight_bold--ePDnv _93444fe79c--fontSize_22px--viEqA '
                                         '_93444fe79c--display_block--pDAEx _93444fe79c--text--g9xAG '
                                         '_93444fe79c--text_letterSpacing__normal--xbqP6').text.split()[:2])
        photo = [photo.get('src') for photo in soup.find_all(class_='_93444fe79c--container--KIwW4')]
        return {'link': link, 'metro': metro, 'price': price, 'photo': photo}
    except AttributeError:
        return None


def get_cards(response):
    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    metro_stations = []
    prices = []
    photos = []

    cards = soup.find_all(class_='_93444fe79c--card--ibP42 _93444fe79c--wide--gEKNN')
    for card in cards:
        info = get_card_info(card)
        if info is not None:
            links.append(info['link'])
            metro_stations.append(info['metro'])
            prices.append(info['price'])
            photos.append(info['photo'])
        else:
            continue

    return {'link': links, 'metro': metro_stations, 'price': prices, 'photo': photos}


def process_all_pages(start_url):
    url = start_url
    links = []
    metro_stations = []
    prices = []
    photos = []
    while True:
        response = requests.get(url)
        cards = get_cards(response)
        links.extend(cards['link'])
        metro_stations.extend(cards['metro'])
        prices.extend(cards['price'])
        photos.extend(cards['photo'])

        soup = BeautifulSoup(response.text, 'html.parser')
        next_page_button = soup.find_all(class_='_93444fe79c--button--Cp1dl _93444fe79c--link-button--Pewgf '
                                                '_93444fe79c--M--T3GjF _93444fe79c--button--dh5GL')[-1]

        if 'Дальше' in next_page_button.text and next_page_button.get('disabled') is None:
            url = next_page_button.get('href')
            if 'spb.cian.ru' not in url:
                url = 'https://spb.cian.ru' + url
        else:
            return {'link': links, 'metro': metro_stations, 'price': prices, 'photo': photos}


def get_image_from_url(url):
    response = requests.get(url)
    return response.content


start_url = "https://spb.cian.ru/cat.php?deal_type=rent&engine_version=2&offer_type=flat&region=2&room1=1&room2=1" \
            "&room3=1&room4=1&room5=1&room6=1&room7=1&room9=1&type=4"
data = process_all_pages(start_url)

conn = sqlite3.connect('rentals.db')
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE rentals (
        id INTEGER PRIMARY KEY,
        link TEXT,
        metro TEXT,
        price TEXT,
        photo BLOB
    )
""")
conn.commit()

for link, metro, price, photo_urls in zip(data['link'], data['metro'], data['price'], data['photo']):
    for photo_url in photo_urls:
        photo = get_image_from_url(photo_url)
        cursor.execute("INSERT INTO rentals VALUES (?, ?, ?, ?)", (link, metro, price, photo))
conn.commit()

conn.close()
