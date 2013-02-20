"""různé pomocné struktury"""
import bottle
from bottle import hook, request

 
@hook("before_request")
def resetLocals():
    """Inicializuje uložiště lokálních dat"""
    request._locals = {}
    
def addMenu(link, desc, _class, priority = 0):
    if not "menu" in request._locals:
        request._locals["menu"] = []
        
    request._locals["menu"].append( (link, desc, _class, priority) )

def _getMenu():
    #seradime podle priority
    sorted( request._locals["menu"], key = lambda x: x[-1] )
    
    return request._locals["menu"]

############

def msg(txt, type = "info"):
    s = request.environ.get('beaker.session')
    if not "msgs" in s:
        s["msgs"] = []

    s["msgs"].append( (txt, type) ) 
    
    s.save()    

def template(*args, **kwargs):
    """Vylepsená funkce pro volani sablony
    
        doplnuje zprávy ze sessions, aktualne prihlaseneho usera a menu
    """
    
    ### zprávy
     
    s = request.environ.get('beaker.session')
    msgs = s.get("msgs", tuple());
    kwargs["msgs"] = msgs
    if msgs:
        s.pop("msgs")
    
    ### uživatel
        
    from user import getUser        
    kwargs["user"] = getUser()
    
    ### menu
    
    kwargs["getMenu"] = _getMenu
    kwargs["requestedURL"] = request.path
        
    return bottle.template(*args, **kwargs) 
    

