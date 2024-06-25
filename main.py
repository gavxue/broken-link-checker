import requests
from bs4 import BeautifulSoup

from modules import Page

url = "https://uwaterloo.ca/civil-environmental-engineering-information-technology"

page = requests.get(url)

soup = BeautifulSoup(page.text, 'html.parser')

menu_links = [Page('Home', url)]

nav = soup.find('nav', {'class': 'uw-header__nav'})
subnav = nav.find_all('ul', {'class': 'menu__subnav'})

for s in subnav:
    links = s.find_all('a', {'class': 'menu__link'})

    for a in links:
        menu_links.append(Page(a.text.strip(), a['href'].strip()))

for x in menu_links:
    print(x.name)
    print(x.url)