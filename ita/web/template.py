from bottle import route, post, request, redirect, response, hook
from helpers import template, msg, addMenu, form_renderer
from user import role, getUser, User

################################################################################
# stránky

@route('/templates')
@role('lector')
def list():
    """Seznam šablon a možnost jejich úpravy"""

    from ita import Loader, Parser, Generator
    l = Loader().add("sablony")
    p = Parser( l )

    return template("templates", {"files" : p.processedPaths})


@route('/templates/<filename:path>', method=['GET', 'POST'])
@role('lector')
def edit(filename):
    
    from ita import Loader
    l = Loader().add("sablony")

    allowed = (path for path, content in l.getPathsOnly() )
    
    if not filename in allowed:
        msg("Integrita narušena","error");
        redirect("/templates");

    content = request.forms.get("content");
    if content:
        try:
            save = l.save
        except AttributeError:
            msg("Současný Loader nepodporuje ukládání","error")
            redirect(request.path)
        save(filename, content)
       
        msg("Změny uloženy","success")
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

