from bottle import route, default_app, request
import os
import sys
from subprocess import call
default_app.push()

@route('/reload')
def gitreload():
    os.system("git pull")
    
    call([sys.executable]+sys.argv, shell=True)
    exit();
    return 'ok'

app = default_app.pop()