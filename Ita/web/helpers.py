"""různé pomocné struktury"""
import bottle
from bottle import hook, request

 
@hook("before_request")
def resetLocals():
    """Inicializuje uložiště lokálních dat pro každý požadavek"""
    request._locals = {}
    
############

def form_renderer(form, action = ""):
    """Vyrenderuje formulář podle zvyklostí bootstrap frameworku"""
    ret = []
    ret.append("<form method='post' action='%s' class='form-horizontal'>" % (action,) )

    for item in form.order:
        itemId = "form"+item
        item = form[item]
        
        ret.append('<div class="control-group">')
        if item.type != "SubmitField":
            ret.append('<label class="control-label" for="%s">%s</label>'%(itemId, item.label) )
        ret.append('<div class="controls">')
        ret.append( item( id=itemId ) )
        ret.append('</div>')
        ret.append('</div>')

    ret.append('</form>')
    return "\n".join(ret)
        
    
############    
    
def addMenu(link, desc, priority = 0, _class = ""):
    """Přidá položku do menu, které je předáváno při každém generování šablony """
    
    if not "menu" in request._locals:
        request._locals["menu"] = []
        
    request._locals["menu"].append( (link, desc, _class, priority) )

def _getMenu():
    """Vrátí seřazené lokální menu """
    #seradime podle priority
    request._locals["menu"] = sorted( request._locals["menu"], key = lambda x: x[-1] )
    
    return request._locals["menu"]

############

def msg(txt, type = "info"):
    """Vloží zprávu k zobrazení"""
    
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
    

