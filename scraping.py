import requests
from bs4 import BeautifulSoup


def get_card_info(card):
    soup = BeautifulSoup(str(card), 'html.parser')

    link = soup.find(class_='_93444fe79c--media--9P6wN').get('href')
    metro = soup.find(class_='_93444fe79c--container--w7txv').find_all('div')[-2].text.strip()
    price = soup.find(class_='_93444fe79c--color_black_100--kPHhJ _93444fe79c--lineHeight_28px--whmWV '
                             '_93444fe79c--fontWeight_bold--ePDnv _93444fe79c--fontSize_22px--viEqA '
                             '_93444fe79c--display_block--pDAEx _93444fe79c--text--g9xAG '
                             '_93444fe79c--text_letterSpacing__normal--xbqP6').text.split()[0]
    photo = soup.find(class_='_93444fe79c--container--KIwW4').get('src')

    return {'link': link, 'metro': metro, 'price': price, 'photo': photo}


def get_cards(response):
    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    metro_stations = []
    prices = []
    photos = []

    cards = soup.find_all(class_='_93444fe79c--card--ibP42 _93444fe79c--wide--gEKNN')
    for card in cards:
        info = get_card_info(card)
        links.append(info['link'])
        metro_stations.append(info['metro'])
        prices.append(info['price'])
        photos.append(info['photo'])

    return {'link': links, 'metro': metro_stations, 'price': prices, 'photo': photos}


url = "https://spb.cian.ru/cat.php?deal_type=rent&engine_version=2&offer_type=flat&region=2&room1=1&room2=1&room3=1" \
      "&room4=1&room5=1&room6=1&room7=1&room9=1&type=4"
response = requests.get(url)

data = get_cards(response)
for i in range(len(data['link'])):
    print('Карточка', i+1)
    print('Ссылка:', data['link'][i])
    print('Станция метро:', data['metro'][i])
    print('Цена:', data['price'][i])
    print('Фото:', data['photo'][i])
    print()
