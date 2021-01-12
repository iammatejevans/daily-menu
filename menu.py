from datetime import datetime

import requests
from bs4 import BeautifulSoup


def zelivarna() -> dict:
    url = "https://developers.zomato.com/api/v2.1/dailymenu?res_id=16506964"
    key = "7f6c07184e81bb5ac0ab62ecf5c7236b"
    headers = {"user_key": key}
    response = requests.get(url, headers=headers)
    daily_menus = response.json()['daily_menus']
    menu_list = []
    for menu in daily_menus:
        try:
            date = datetime.strptime((menu['daily_menu']['start_date']).split(' ')[0], "%Y-%m-%d")
            if date.date() == datetime.now().date():
                for dish in menu['daily_menu']['dishes']:
                    menu_item = {'name': dish['dish']['name'].strip().capitalize(),
                                 'description': '',
                                 'price': dish['dish']['price'].strip().replace('\xa0', ' ').capitalize()}
                    menu_list.append(menu_item)
        except (IndexError, KeyError):
          pass
    desc = '(příplatek za krabici hl. jídlo: 10 Kč, polévka: 3 Kč)'
    return {'name': 'Želivárna', 'url': url, 'description': desc, 'menu': menu_list}


def u_sedlacku():
    url = "http://www.usladecku.cz/denni-menu/"
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:81.0) Gecko/20100101 Firefox/81.0'}
    menu_page = requests.get(url, headers=headers)
    menu_page.encoding = 'utf-8'
    menu_soup = BeautifulSoup(menu_page.text, 'html.parser')
    menu_div = menu_soup.select('.sidebar_content')

    menu_list = []

    if menu_div:
        try:
            page_date = menu_div[0].findChildren('i')[0].text.split(" ")[1]
            if datetime.strptime(page_date.strip(), '%d.%m.%Y').date() == datetime.today().date():
                for item in [x.findChildren('td') for x in menu_div[0].findChildren('table')]:
                    for i in range(0, len(item), 2):
                        try:
                            item_list = item[i].text.replace('\xa0', '').strip().split('\n\n')
                            if not [x for x in item_list if x]:
                                continue
                            if len(item_list) > 1:
                                for x in range(len(item_list)):
                                    price_list = item[i + 1].text.replace('\xa0', '').strip().split('\n\n')
                                    if len(price_list) > 1:
                                        menu_item = {
                                            'name': item_list[x].replace('2. ', '').replace('3. ', '').capitalize(),
                                            'description': '',
                                            'price': price_list[x]
                                        }
                                        menu_list.append(menu_item)
                                    continue
                                continue

                            menu_item = {'name': item_list[0].replace('1. ', '').replace('4. ', '').capitalize()}
                        except IndexError:
                            menu_item = {}

                        try:
                            price = item[i+1].text.replace('\xa0', '').strip()
                        except IndexError:
                            price = ''

                        menu_item['description'] = ""
                        menu_item['price'] = price
                        menu_list.append(menu_item)
                        
            except (IndexError, KeyError):
                pass

    desc = '(příplatek za krabici hl. jídlo: 10 Kč, polévka: 10 Kč)'
    return {'name': 'U Sládečků', 'url': url, 'description': desc, 'menu': menu_list}


def potrefena_husa():
    url = "http://www.potrefene-husy.cz/cz/vinohrady-poledni-menu"
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:81.0) Gecko/20100101 Firefox/81.0'}
    menu_page = requests.get(url, headers=headers)
    menu_soup = BeautifulSoup(menu_page.text, 'html.parser')
    menu_div = menu_soup.select('.poledni-nabidka table')[0]

    menu_list = []

    weekdays = [
        'neděle',
        'pondělí',
        'úterý',
        'středa',
        'čtvrtek',
        'pátek',
        'sobota'
    ]

    if menu_div:
        try:
            day = None

            for child in [x for x in menu_div.findChildren('h3') if x.text.lower() in weekdays]:
                if weekdays.index(child.text.lower()) == int(datetime.strftime(datetime.today(), '%w')):
                    day = child.text
                    break

            all_menus = [x for x in menu_div.findChildren('tr')]
            result = []
            for child in all_menus:
                if day not in [x.text for x in child]:
                    continue
                else:
                    day_index = [x.text for x in [a for a in all_menus]].index(child.text)
                    result = all_menus[day_index+1:day_index+5]
                    break

            for item in result:
                menu_item = {
                    'name': item.select(".tdii")[0].text,
                    'description': (item.select(".tdi")[0]
                                   .text.replace('Menu I.', '')
                                   .replace('Menu II.', '')
                                   .replace('Menu ll.', '')
                                   .replace('Menu III.', '')
                                   .replace('/', '')
                                   .replace('.', '')),
                    'price': item.select(".tdiii")[0].text
                }
                menu_list.append(menu_item)
                
          except (IndexError, KeyError):
              pass

    desc = '(příplatek za krabici: 10 Kč)'
    return {'name': 'Potrefená Husa', 'url': url, 'description': desc, 'menu': menu_list}


def vidlicky_a_noze():
    url = "https://www.vidlickyanoze.com/"
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:81.0) Gecko/20100101 Firefox/81.0'}
    menu_page = requests.get(url, headers=headers)
    menu_page.encoding = 'utf-8'
    menu_soup = BeautifulSoup(menu_page.text, 'html.parser')
    menu_div = menu_soup.select("#daily")[0].select('.row')[1:]

    menu_list = []

    if menu_div:
    
        try:
            for item in menu_div:
                menu_item = {
                    'name': item.select(".food-title")[0].text,
                    'description': '',
                    'price': item.select(".food-price")[0].text.replace('\xa0', ' ')
                }
                menu_list.append(menu_item)
        except (IndexError, KeyError):
            pass

    desc = '(příplatek za krabici: 10 Kč)'
    return {'name': 'Vidličky a nože', 'url': url, 'description': desc, 'menu': menu_list}


def get_daily_menu():
    html = ["<p style='font-family: Arial; font-size:10pt;'>Dobrý den / Ahoj, posílám Vám dnešní obědové menu:</p><ul>"]

    for restaurant in [zelivarna(), u_sedlacku(), potrefena_husa(), vidlicky_a_noze()]:
        name = restaurant["name"]
        url = restaurant["url"]
        description = restaurant["description"]
        menu = restaurant["menu"]

        html.append(f"<li><p><a href='{url}' style='font-family: Arial; font-size:10pt; color:black;'>{name}</a></p>")
        html.append(f"<span style='font-family: Arial; font-size:10pt;'>{description}</span>")
        html.append("<ul>")

        for item in menu:
            food_name = item["name"]
            food_description = item["description"]
            food_price = item["price"]

            html.append(f"<li style='font-family: Arial; font-size:10pt;'>{food_name}")
            if food_description:
                html.append(f" ({food_description})")
            html.append(f" ({food_price})</li>")

        html.append("</ul></li><br>")

    html.append("<li><p style='font-family: Arial; font-size:10pt;'>Stálá nabídka</p>")
    html.append("<ul><li><p style='font-family: Arial; font-size:10pt;'>"
                "<a href='https://www.pizzaexpresspraha.cz/stranky/intro.php#utm_source=mapy.cz&utm_medium="
                "ppd&utm_content=hledani&utm_term=%C5%BEelivsk%C3%A9ho&utm_campaign=firmy.cz-12927762' "
                "style='font-family: Arial; font-size:10pt; color:black;'>Pizza Express")
    html.append("</a> (příplatek za krabici pizza velká 13Kč, pizza malá 7Kč)</p></li></ul></li></ul>")

    return "".join(html)


if __name__ == "__main__":
    get_daily_menu()
