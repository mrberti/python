from flask import render_template
from werkzeug.serving import WSGIRequestHandler
from app import app

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Miguel'}
    return render_template('index.html', title='Home', user=user)

WSGIRequestHandler.protocol_version = "HTTP/1.1"