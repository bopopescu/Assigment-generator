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
    from ita import ita_parser
    from ita import generator
    p = ita_parser.Parser()
    p.loadDir(root)

    return template("templates", {"files" : p.files, "root":root})


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
    

    return template("templates_edit", root = pathToModule+"/static/")


@route('/groups/edit/<group_id:int>', method=['GET', 'POST'])
@role('lector')    
def edit(group_id):
    """Úprava specifické skupiny včetně přidávání uživatelů"""
    
    group = Group.get( group_id )
    
    # vložení studenta
    if request.forms.get("add"):
        usr = User( request.forms.get("add") )
        try:
            usr.insert( group_id )
            msg("Student %s vložen" % usr.login,"success")
        except Exception as e: 
            msg("Chyba při vkládání studenta - %s " % e,"error")                   
                

        redirect(request.path)
    
    # odstranění studenta
    if request.query.get("remove"):
        usr = User( request.query.get("remove") )

        if usr.remove():
            msg("Student %s odstraněn"% usr.login ,"success")
        else:
            msg("Student nenalezen","error")

        redirect(request.path)
        
    form = GroupForm(request.forms.decode(), group)
    
    if request.method == 'POST' and form.validate():
        try:
            group.update( name = form.name.data )
            msg("Skupina aktualizována","success")
        except Exception as e:
            msg("Chyba při aktualizaci - %s" % e, "error")
        
        redirect(request.path)    
            
    
            
            
    return template("groups_edit", {"group" : group, "form": form_renderer(form) } )    
    
###############################################################################
# callbacky

@hook("before_request")
def groupMenu():
    usr = getUser() 

    if usr and usr.inRole("lector"):
        addMenu("/templates","Šablony",90)

