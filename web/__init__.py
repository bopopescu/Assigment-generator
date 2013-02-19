import sys
import os

# bad practice - do NOT try this at home
# nicmene to vycisti top level adresar a neni potreba moduly instalovat
# diky tomu je cela aplikace zavisla jenom na Pythonu...
  
path = os.path.dirname(__file__)
sys.path.append(path)

import bottle
from beaker.middleware import SessionMiddleware

from . import config
from .frontend import app as frontendApp

from .database import DBPlugin

mainApp = frontendApp

db = DBPlugin()
mainApp.install(db)


mainApp = SessionMiddleware(mainApp , config.session_opts)

def run(**kwargs):
    kwargs["app"] = mainApp

    bottle.debug(True)
    bottle.run(**kwargs)



__all__ = ["run"]