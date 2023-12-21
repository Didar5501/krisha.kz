import requests
from bs4 import BeautifulSoup
import re
import json

data_list = []
district_data = {}  

for i in range(1, 4):
    print(f'Парсим {i}-ю стр...')

    url = f'https://krisha.kz/arenda/kvartiry/almaty/?das[live.rooms]={i}'

    response = requests.get(url)

    soup = BeautifulSoup(response.text, 'lxml')
    cards = soup.find_all('div', class_='a-card__inc')
    count = 0
    for card in cards[:5]:

        card_url = card.a['href']

        url = f'https://krisha.kz/{card_url}'

        url_parts = url.split('/')
        ad_id = url_parts[-1]

        response = requests.get(url=url)

        soup = BeautifulSoup(response.text, 'lxml')

        layout__content = soup.find('div', class_='layout__content')
        title = layout__content.find('h1')
        title_text = title.text.strip()

        short_description = soup.find('div', class_='offer__short-description')
        region = short_description.find('span')

        offer__price = soup.find("div", class_='offer__price')
        price_text = offer__price.text.strip()
        match = re.search(r'\d+', price_text)
        price = match.group() + '000' if match else 'Не указано'
        author = soup.find("div", class_='owners__name')
        author_text = author.text if author else 'Не указано'

        count += 1

        ad_dict = {
            "Объявление №": count,
            "ID объявления": ad_id,
            "Ссылка": url,
            "Заголовок объявления": title_text,
            "Автор объявления": author_text,
            "Район": region.text,
            "Цена": price
        }

        data_list.append(ad_dict)

    
        district = region.text.strip()
        if district not in district_data:
            district_data[district] = {
                "кол-во объявлений": 0,
                "макс цена": 0,
                "мин цена": float('inf'),
                "сред цена": 0
            }

        district_data[district]["кол-во объявлений"] += 1
        district_data[district]["макс цена"] = max(district_data[district]["макс цена"], int(price))
        district_data[district]["мин цена"] = min(district_data[district]["мин цена"], int(price))
        district_data[district]["сред цена"] += int(price)


for district, data in district_data.items():
    if data["кол-во объявлений"] > 0:
        data["сред цена"] = data["сред цена"] // data["кол-во объявлений"]


with open('Svodka.json', 'w', encoding='utf-8') as json_file:
    json.dump(district_data, json_file, ensure_ascii=False, indent=4)

print("Данные записаны в Svodka.json")


with open('krisha_data.json', 'w', encoding='utf-8') as json_file:
    json.dump(data_list, json_file, ensure_ascii=False, indent=4)

print("Данные записаны в krisha_data.json")