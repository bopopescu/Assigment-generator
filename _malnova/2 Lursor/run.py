#! /usr/bin/python3
from bottle import route, run, view
from generator import Generator
import codecs

@route('/')
@view("index")
def index():
    data = {}

    g = Generator()
    g.loadDir("base")
    g.loadDir("cviceni3")


    data["output"] = g.expand("{cviceni}")
    
    return data

run(host='0.0.0.0', port=8080)
