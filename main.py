import requests
from bs4 import BeautifulSoup

class Page:
    def __init__(self, name, url):
        self.name = name
        self.url = url

url = "https://uwaterloo.ca/civil-environmental-engineering-information-technology"

homepage = requests.get(url)

soup = BeautifulSoup(homepage.text, 'html.parser')

# scraping pages
menu_links = [Page('Home', url)]

nav = soup.find('nav', {'class': 'uw-header__nav'})
subnav = nav.find_all('ul', {'class': 'menu__subnav'})

for s in subnav:
    links = s.find_all('a', {'class': 'menu__link'})

    for a in links:
        menu_links.append(Page(a.text.strip(), "https://uwaterloo.ca" + a['href'].strip()))


# checking pages
for menu_link in menu_links:
    # print(menu_link.name)
    # print(menu_link.url)
    page = requests.get(menu_link.url)
    page_soup = BeautifulSoup(page.text, 'html.parser')
    main = page_soup.find('main')
    links = main.find_all('a')

    for link in links:
        if 'href' not in link.attrs:
            print('ERROR - NO HREF FOUND')
            continue
        if "https://" not in link['href']:
            print('ERROR - MUST USE ABSOLUTE URL')
            continue

        try:
            res = requests.get(link['href'])
            status = str(res.status_code).strip()
            print('HTTP ' + status)
        except requests.exceptions.HTTPError as errh:
            print ("Http Error:",errh)
        except requests.exceptions.ConnectionError as errc:
            print ("Error Connecting:",errc)
        except requests.exceptions.Timeout as errt:
            print ("Timeout Error:",errt)
        except requests.exceptions.RequestException as err:
            print ("OOps: Something Else",err)

