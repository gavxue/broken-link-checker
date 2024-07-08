from flask import Flask, render_template, request
from main import check, Page

app = Flask(__name__)
app.config['DEBUG'] = True

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        messages = check()
        return render_template('output.html', messages=messages)
    
    return render_template('index.html')