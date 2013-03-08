from bottle import route, default_app, request, static_file, hook
from helpers import template, msg, addMenu
from user import getUser
import os

pathToModule = os.path.dirname(__file__)

import user
import group
import lecture
import assigment
import template

@route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root = pathToModule+"/static/")

@route("/")
def index():
    return template("index")

app = default_app.pop()
