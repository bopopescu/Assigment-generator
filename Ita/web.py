#! /usr/bin/python3
from bottle import route, run, view
from generator import Generator
from ita_parser import Parser

@route('/')
@view("index")
def index():
    p = Parser()

    p.loadDir("base")
    p.loadDir("cviceni3")

    g = Generator( p.rules )
    
    return {"output":g.run("cviceni")}

run(host='0.0.0.0', port=8080)
