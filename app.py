from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, emit
from threading import Lock
import requests
from bs4 import BeautifulSoup

# from main import check, Page

class Page:
    def __init__(self, name, url):
        self.name = name
        self.url = url

async_mode = None

app = Flask(__name__)
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

# url = 'https://api.coinbase.com/v2/prices/btc-usd/spot'

menu_links = []
results = []

def background_thread():
    global menu_links
    global results
    for menu_link in menu_links:    
        results.append(menu_link.name)
        print(menu_link.url)
        page = requests.get(menu_link.url)
        page_soup = BeautifulSoup(page.text, 'html.parser')
        main = page_soup.find('main')
        links = main.find_all('a')

        for link in links:
            line = link.text.strip() + ' --- '

            if 'href' not in link.attrs:
                line += 'ERROR (NO HREF FOUND)'
                results.append(line)
                continue
            if 'mailto:' in link['href']:
                line += 'MAIL LINK (NEEDS MANUAL CHECK)'
                results.append(line)
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

            results.append(line)

            socketio.emit('my_response', {'data': line})


    # count = 0
    # while True:
    #     socketio.sleep(3)
    #     count += 1
    #     price = ((requests.get(url)).json())['data']['amount']
    #     socketio.emit('my_response', {'data': 'Bitcoin current price (USD): ' + price, 'count': count})


@app.route('/', methods=['GET', 'POST'])
def index():
    # if request.method == 'POST':
    #     messages = check()
    #     return render_template('output.html', messages=messages)
    
    return render_template('index.html', async_mode=socketio.async_mode)


@socketio.event
def my_event(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})

# Receive the test request from client and send back a test response
@socketio.on('test_message')
def handle_message(data):
    print('received message: ' + str(data))
    emit('test_response', {'data': 'Test response sent'})

# Broadcast a message to all clients
@socketio.on('broadcast_message')
def handle_broadcast(data):
    print('received: ' + str(data))
    emit('broadcast_response', {'data': 'Broadcast sent'}, broadcast=True)

@socketio.event
def connect():
    global menu_links
    my_url = "https://uwaterloo.ca/civil-environmental-engineering-information-technology"

    homepage = requests.get(my_url)

    soup = BeautifulSoup(homepage.text, 'html.parser')

    # scraping pages
    menu_links = [(Page('Home', my_url))]
    nav = soup.find('nav', {'class': 'uw-header__nav'})
    subnav = nav.find_all('ul', {'class': 'menu__subnav'})

    for s in subnav:
        links = s.find_all('a', {'class': 'menu__link'})

        for a in links:
            menu_links.append(Page(a.text.strip(), "https://uwaterloo.ca" + a['href'].strip()))

    # print(menu_links)

    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})

if __name__ == '__main__':
    socketio.run(app)

