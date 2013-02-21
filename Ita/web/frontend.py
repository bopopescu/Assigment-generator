from bottle import route, default_app, request, static_file, hook
from helpers import template, msg, addMenu
from user import getUser
import os

pathToModule = os.path.dirname(__file__)

#import user
from user import role

@route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root = pathToModule+"/static/")

@route('/')
@role("student")
def test(db):
  s = request.environ.get('beaker.session')
  s['test'] = s.get('test',0) + 1
  s.save()
  
  return template("index")
  

@route('/generate')
@role("student")
def generate(db):
    from .. import ita_parser
    from .. import generator

    p = ita_parser.Parser()

    p.loadDir("ita/base")
    p.loadDir("ita/cviceni3")

    g = generator.Generator( p.rules )
    
    return template("generate", {"cviceni":g.run("cviceni")} )  
  
  



###############################################################################
# callbacky

@hook("before_request")
def userMenu():
    usr = getUser() 
    if usr:
        addMenu("/generate","Zadání",50)


   


app = default_app.pop()
