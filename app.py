from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from threading import Lock
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

menu_links = []

def background_thread():
    global menu_links
    for menu_link in menu_links:    
        result = []
        page = requests.get(menu_link.url)
        page_soup = BeautifulSoup(page.text, 'html.parser')
        main = page_soup.find('main')
        links = main.find_all('a')

        for link in links:
            line = link.text.strip() + ' --- '

            if 'href' not in link.attrs:
                line += 'ERROR (NO HREF FOUND)'
                result.append(line)
                continue
            if 'mailto:' in link['href']:
                line += 'MAIL LINK (NEEDS MANUAL CHECK)'
                result.append(line)
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

            result.append(line)

            socketio.emit('my_response', {'data': line})


@app.route('/')
def index():  
    return render_template('index.html')


@app.route('/results', methods=['POST'])
def results():
    socketio.run(app, debug=True, port=5004)
    print(request.form.get('url'))
    return render_template('results.html', async_mode=socketio.async_mode)


@app.route('/stop', methods=["POST"])
def stop():
    socketio.stop()
    return 'Automation as been stopped'


@socketio.event
def my_event(message):
    emit('my_response',
         {'data': message['data']})


@socketio.event
def connect():
    global menu_links
    my_url = "https://uwaterloo.ca/civil-environmental-engineering"

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

    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    emit('my_response', {'data': 'Connected'})

# if __name__ == '__main__':
#     socketio.run(app, debug=True, port=5004)

