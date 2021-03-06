from bottle import route, default_app, request, static_file, hook, redirect
from helpers import template, msg, addMenu
from user import getUser
import os

pathToModule = os.path.dirname(__file__)

import user
import group
import lecture
import assigment
import template as templateWeb  # abychom se vyhnuli kolizi s helper fnc

@route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root = pathToModule+"/static/")

@route("/")
def index():
    usr = getUser()
    if usr and usr.inRole("student"):
        redirect("/assigments")
    return template("index")

app = default_app.pop()
