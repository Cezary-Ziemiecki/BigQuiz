from flask import Flask, render_template
import os
from app.quiz.controllers import blueprint as quiz_blueprint
from .web import blueprint as web_blueprint
import requests

from subprocess import Popen, PIPE

template_dir = os.path.abspath('app/templates')
static_dir = os.path.abspath('app/static')
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
# app.config['SECRET_KEY'] = 'xxxx'

app.register_blueprint(web_blueprint)
app.register_blueprint(quiz_blueprint, url_prefix='/quiz')


@app.route('/')  # Strona glowna
def index():
    return render_template('home.html')
