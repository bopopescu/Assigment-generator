from bottle import route, default_app, request

default_app.push()

import user
from user import role


@route('/')
@role("student")
def test(db):
  s = request.environ.get('beaker.session')
  s['test'] = s.get('test',0) + 1
  s.save()

  return 'Test counter2: %d' % s['test']


app = default_app.pop()
