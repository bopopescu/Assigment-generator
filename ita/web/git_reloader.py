from bottle import route, default_app, request
import os
import sys

default_app.push()

@route('/reload')
def gitreload():
    os.system("git pull")
    os.execv(sys.executable, [sys.argv[0]]+sys.argv)
    return 'ok'

app = default_app.pop()