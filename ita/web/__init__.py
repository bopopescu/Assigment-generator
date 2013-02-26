import sys
import os

# bad practice - do NOT try this at home
# nicmene to vycisti top level adresar a neni potreba moduly instalovat
# diky tomu je cela aplikace zavisla jenom na Pythonu...
  
path = os.path.dirname(__file__)
sys.path.append(path)

import bottle

# přidáme views z aktuálního adresáře
bottle.TEMPLATE_PATH.append( path+"/views/")

from beaker.middleware import SessionMiddleware

from . import config
from .frontend import app as frontendApp

from .database import DBPlugin

################################################################################

from git_reloader import app as gitReloader

mainApp = frontendApp
mainApp.mount("/git/", gitReloader)

db = DBPlugin()
mainApp.install(db)
mainApp = SessionMiddleware(mainApp , config.session_opts)

def run(**kwargs):
    kwargs["app"] = mainApp

    bottle.debug(True)
    bottle.run(**kwargs)



__all__ = ["run"]