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
        status = "text-danger"

        if 'href' not in link.attrs:
            line += 'ERROR (NO HREF FOUND)'
        elif 'mailto:' in link['href']:
            line += 'MAIL LINK (NEEDS MANUAL CHECK)'
            status = 'text-warning'
        else:
            if "https://" not in link['href']:
                # line += 'ERROR - MUST USE ABSOLUTE URL'
                # continue
                link['href'] = 'https://uwaterloo.ca' + link['href']

            try:
                res = requests.get(link['href'], timeout=10)
                status_code = str(res.status_code).strip()
                line += 'HTTP ' + status_code
                if status_code == '200':
                    status = 'text-success'
            except requests.exceptions.HTTPError:
                line += "HTTP ERROR"
            except requests.exceptions.ConnectionError:
                line += "ERROR CONNECTING"
            except requests.exceptions.Timeout:
                line += "TIMEOUT ERROR"
            except requests.exceptions.RequestException:
                line += "UNKNOWN ERROR"

        # log link status
        socketio.emit('response', {'message': line, 'class': status})

        if not event.is_set():
            return False

    return True


def background_thread(event):
    global thread

    try:
        if event.is_set():
            homepage = requests.get(url)
            soup = BeautifulSoup(homepage.text, 'html.parser')

            # homepage
            socketio.emit('response', {'message': "Home", 'class': 'section'})
            check_page(url, event)

            navs = soup.find_all('nav', {'class': 'uw-horizontal-nav'})

            # main nav
            nav = navs[1].find('ul')
            menu_items = nav.find_all('li', {'class': 'menu__item'}, recursive=False)

            for menu_item in menu_items:
                # log section
                menu_item_title = menu_item.find('a').text.strip()
                socketio.emit('response', {'message': menu_item_title, 'class': 'section'})
                submenu_items = menu_item.find_all('a', href=True)
                
                for submenu_item in submenu_items:
                    # log section item
                    socketio.emit('response', {'message': submenu_item.text.strip(), 'class': 'page'})
                    live = check_page('https://uwaterloo.ca' + submenu_item.get('href').strip(), event)

                    if not live:
                        return

            # secondary nav (if exists)
            if len(navs) == 3:
                sec_nav = navs[2].find('ul')
                menu_items = sec_nav.find_all('li', {'class': 'menu__item'}, recursive=False)

                for menu_item in menu_items:
                    # log section
                    menu_item_title = menu_item.find('a').text.strip()
                    socketio.emit('response', {'message': menu_item_title, 'class': 'section'})
                    submenu_items = menu_item.find_all('a', href=True)
                    
                    for submenu_item in submenu_items:
                        # log section item
                        socketio.emit('response', {'message': submenu_item.text.strip(), 'class': 'page'})
                        live = check_page('https://uwaterloo.ca' + submenu_item.get('href').strip(), event)

                        if not live:
                            return
            
            # log completion
            socketio.emit('response', {'message': 'Success!'})

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
    emit('response',
         {'message': message['data']})


@socketio.event
def connect():
    emit('response', {'message': 'Connected'})

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

