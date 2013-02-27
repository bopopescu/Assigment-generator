from bottle import route, default_app, request, Bottle
import os
import sys

default_app.push()

@route('/reload')
def gitreload():
    Bottle.close()
    os.system("git pull")
    os.execv(sys.executable, [sys.argv[0]]+sys.argv)
    return 'ok'

app = default_app.pop()