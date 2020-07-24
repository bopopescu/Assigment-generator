import sys
import os

# bad practice - do NOT try this at home
# nicmene to vycisti top level adresar a neni potreba moduly instalovat
# diky tomu je cela aplikace zavisla jenom na Pythonu, coz je priorita zadani...
  
path = os.path.dirname(__file__)
sys.path.append(path)


################################################################################
# označeni aktualni revize
print("Trying to detect main reference")
VERSION_CONTROL = "unknown"
try:
    import subprocess
    label = subprocess.check_output(["git", "rev-parse","HEAD"], shell=True)
    VERSION_CONTROL = label.decode("ascii").strip()
except:
    pass    

print("Reference resolved",VERSION_CONTROL )
################################################################################

import bottle

# přidáme views z aktuálního adresáře
bottle.TEMPLATE_PATH.append( path+"/views/")

from beaker.middleware import SessionMiddleware

from . import config
from .frontend import app as frontendApp

################################################################################

mainApp = frontendApp


mainApp = SessionMiddleware(mainApp , config.session_opts)

def run(**kwargs):
    params = {"host": "0.0.0.0", "port": "8080", "app": mainApp, "server": "rocket", "debug":True }
    params.update(kwargs)
    
    bottle.debug(params["debug"])
    
    if params["server"] == "default":
        params.pop("server")
        bottle.run(**params)
    elif params["server"] == "rocket":
        from ita.web.rocket  import Rocket
        server = Rocket((params["host"], params["port"]), 'wsgi', { 'wsgi_app' : mainApp })
        server.start()
    else:
        raise RuntimeException("Nerozpoznany server");



__all__ = ["run", "VERSION_CONTROL"]