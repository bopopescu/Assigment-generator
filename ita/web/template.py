from bottle import route, post, request, redirect, response, hook
from helpers import template, msg, addMenu, form_renderer
from user import role, getUser, User

################################################################################
# stránky

@route('/templates')
@role('lector')
def list():
    """Seznam šablon a možnost jejich úpravy"""
    #todo: do configu ?
    root = "ita/sablony"
    
    #todo: hezci pristup k parsovani
    from ita import Loader, Parser, Generator
    l = Loader().add(root)
    p = Parser( l )
    p.parse()

    return template("templates", {"files" : p.processedPaths, "root":root})


@route('/templates/<filename:path>', method=['GET', 'POST'])
@role('lector')
def edit(filename):

    from ita import ita_parser
    from ita import generator
    p = ita_parser.Parser()
    p.loadDir("ita/sablony")
    allowed = p.files.keys()
    
    if not filename in allowed:
        msg("Integrita narušena","error");
        redirect("/templates");

    if request.forms.get("content"):
        msg("Nemáte oprávnění ukládat šablony","error")
        redirect(request.path)
    
    
    with open(filename, "rb") as f:
        content = b"".join( f.readlines() ) 

    return template("templates_edit", content = content )

    
###############################################################################
# callbacky

@hook("before_request")
def groupMenu():
    usr = getUser() 

    if usr and usr.inRole("lector"):
        addMenu("/templates","Šablony",90)

