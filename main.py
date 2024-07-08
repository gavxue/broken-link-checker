import requests
from bs4 import BeautifulSoup

class Page:
    def __init__(self, name, url):
        self.name = name
        self.url = url


def check():
    url = "https://uwaterloo.ca/civil-environmental-engineering-information-technology"

    homepage = requests.get(url)

    soup = BeautifulSoup(homepage.text, 'html.parser')

    # scraping pages
    menu_links = [(Page('Home', url))]
    nav = soup.find('nav', {'class': 'uw-header__nav'})
    subnav = nav.find_all('ul', {'class': 'menu__subnav'})

    for s in subnav:
        links = s.find_all('a', {'class': 'menu__link'})

        for a in links:
            menu_links.append(Page(a.text.strip(), "https://uwaterloo.ca" + a['href'].strip()))
            # menu_links.append({"name": a.text.strip(), "url": "https://uwaterloo.ca" + a['href'].strip()})

    load = []

    # checking pages
    for menu_link in menu_links:       
        load.append(menu_link.name)
        page = requests.get(menu_link.url)
        page_soup = BeautifulSoup(page.text, 'html.parser')
        main = page_soup.find('main')
        links = main.find_all('a')

        for link in links:
            line = link.text.strip() + ' --- '

            if 'href' not in link.attrs:
                line += 'ERROR (NO HREF FOUND)'
                load.append(line)
                continue
            if 'mailto:' in link['href']:
                line += 'MAIL LINK (NEEDS MANUAL CHECK)'
                load.append(line)
                continue
            if "https://" not in link['href']:
                # line += 'ERROR - MUST USE ABSOLUTE URL'
                link['href'] = 'https://uwaterloo.ca' + link['href']

            try:
                res = requests.get(link['href'])
                status = str(res.status_code).strip()
                line += 'HTTP ' + status
            except requests.exceptions.HTTPError as errh:
                line += "HTTP ERROR"
            except requests.exceptions.ConnectionError as errc:
                line += "ERROR CONNECTING"
            except requests.exceptions.Timeout as errt:
                line += "TIMEOUT ERROR"
            except requests.exceptions.RequestException as err:
                line += "UNKNOWN ERROR"

            load.append(line)
            # print(line)

    return load