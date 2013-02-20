from bottle import route, default_app, request, static_file
from helpers import template,msg
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

  msg("muhehe")
  
  return template("index",{"count" : s['test']}) 


app = default_app.pop()
