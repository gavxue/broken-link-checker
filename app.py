from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from threading import Lock, Event
import requests
from bs4 import BeautifulSoup

class Page:
    def __init__(self, name, url):
        self.name = name
        self.url = url

async_mode = None

app = Flask(__name__)
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()
thread_event = Event()

menu_links = []
url = ""

def check_page(url, event):
    page = requests.get(url)
    page_soup = BeautifulSoup(page.text, 'html.parser')
    main = page_soup.find('main')
    links = main.find_all('a')

    for link in links:
        line = link.text.strip() + ' --- '

        if 'href' not in link.attrs:
            line += 'ERROR (NO HREF FOUND)'
            continue
        if 'mailto:' in link['href']:
            line += 'MAIL LINK (NEEDS MANUAL CHECK)'
            continue
        if "https://" not in link['href']:
            line += 'ERROR - MUST USE ABSOLUTE URL'
            continue
            # link['href'] = 'https://uwaterloo.ca' + link['href']

        try:
            res = requests.get(link['href'], timeout=10)
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

        # log link status
        socketio.emit('my_response', {'data': line})

        if not event.is_set():
            return False

    return True


def background_thread(event):
    global thread

    try:
        if event.is_set():
            homepage = requests.get(url)

            soup = BeautifulSoup(homepage.text, 'html.parser')

            # scraping pages
            # menu_links = [(Page('Home', url))]
            nav = soup.find_all('nav', {'class': 'uw-horizontal-nav'})[1].find('ul')
            menu_items = nav.find_all('li', {'class': 'menu__item'}, recursive=False)

            for menu_item in menu_items:
                # log section
                menu_item_title = menu_item.find('a').text.strip()
                socketio.emit('my_response', {'data': menu_item_title})
                submenu_items = menu_item.find_all('a', href=True)
                
                for submenu_item in submenu_items:
                    # log section item
                    socketio.emit('my_response', {'data': submenu_item.text.strip()})
                    live = check_page('https://uwaterloo.ca' + submenu_item.get('href').strip(), event)

                    if not live:
                        return
            
            # log completion
            socketio.emit('my_response', {'data': 'Success!'})


            # links = nav.find_all('a', {'class': 'menu__link'})
            # for a in links:
            #     try:
            #         menu_links.append(Page(a.text.strip(), "https://uwaterloo.ca" + a['href'].strip())) 
            #     except:
            #         continue

            # subnav = nav.find_all('ul', {'class': 'menu__subnav'})

            # for s in subnav:
            #     links = s.find_all('a', {'class': 'menu__link'})

                # for a in links:
                #     menu_links.append(Page(a.text.strip(), "https://uwaterloo.ca" + a['href'].strip()))

            # for menu_link in menu_links:
            #     socketio.emit('my_response', {'data': menu_link.name})    
                # page = requests.get(menu_link.url)
                # page_soup = BeautifulSoup(page.text, 'html.parser')
                # main = page_soup.find('main')
                # links = main.find_all('a')

                # for link in links:
                #     line = link.text.strip() + ' --- '

                #     if 'href' not in link.attrs:
                #         line += 'ERROR (NO HREF FOUND)'
                #         continue
                #     if 'mailto:' in link['href']:
                #         line += 'MAIL LINK (NEEDS MANUAL CHECK)'
                #         continue
                #     if "https://" not in link['href']:
                #         line += 'ERROR - MUST USE ABSOLUTE URL'
                #         continue
                #         # link['href'] = 'https://uwaterloo.ca' + link['href']

                #     try:
                #         res = requests.get(link['href'], timeout=10)
                #         status = str(res.status_code).strip()
                #         line += 'HTTP ' + status
                #     except requests.exceptions.HTTPError as errh:
                #         line += "HTTP ERROR"
                #     except requests.exceptions.ConnectionError as errc:
                #         line += "ERROR CONNECTING"
                #     except requests.exceptions.Timeout as errt:
                #         line += "TIMEOUT ERROR"
                #     except requests.exceptions.RequestException as err:
                #         line += "UNKNOWN ERROR"

                #     socketio.emit('my_response', {'data': line})

                #     if not event.is_set():
                #         return
    finally:
        event.clear()
        thread = None


@app.route('/')
def index():  
    return render_template('index.html')


@app.route('/results', methods=['POST'])
def results():
    global url
    url = request.form.get('url')
    return render_template('results.html', async_mode=socketio.async_mode)


@socketio.event
def my_event(message):
    emit('my_response',
         {'data': message['data']})


@socketio.event
def connect():
    emit('my_response', {'data': 'Connected'})

    # global menu_links

    # homepage = requests.get(url)

    # soup = BeautifulSoup(homepage.text, 'html.parser')

    # # scraping pages
    # menu_links = [(Page('Home', url))]
    # nav = soup.find('nav', {'class': 'uw-header__nav'})
    # subnav = nav.find_all('ul', {'class': 'menu__subnav'})

    # for s in subnav:
    #     links = s.find_all('a', {'class': 'menu__link'})

    #     for a in links:
    #         menu_links.append(Page(a.text.strip(), "https://uwaterloo.ca" + a['href'].strip()))

    global thread
    with thread_lock:
        if thread is None:
            thread_event.set()
            thread = socketio.start_background_task(background_thread, thread_event)


@socketio.event
def stop():
    global thread
    thread_event.clear()
    with thread_lock:
        if thread is not None:
            thread.join()
            thread = None
    

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5004)

