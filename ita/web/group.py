from bottle import route, post, request, redirect, response, hook
import database
from helpers import template, msg, addMenu, form_renderer
from user import role, getUser, User

################################################################################
# model

from models import Group
    
        
################################################################################
# Formulář        
from wtforms import Form, BooleanField, TextField,SubmitField, validators

class GroupForm(Form):
    order = ["name", "submit"]
    name = TextField('Název', [validators.Length(min=1, max=40)])
    submit  = SubmitField('Uložit')
        
################################################################################
# stránky

@route('/groups', method=['GET', 'POST'])
@role('lector')
def list():
    """Seznam skupin"""
    
    usr = getUser() 
    
    # vložení nové skupiny
    if request.forms.get("add"):
        grp = Group.insert( request.forms.decode().get("add"), usr.login )
        if grp:
            msg("Skupina %s vytvořena" % grp.name,"success")
            redirect("/groups/edit/%i" % grp.group_id )
        else:
            msg("Chyba při vytváření skupiny","error")
            redirect(request.path)
        
    groups = Group.getAll() if usr.inRole("master") else Group.getAll(usr.login) 
    
    return template("groups", {"groups" : groups, "showLector": usr.inRole("master") } )

@route('/groups/edit/<group_id:int>', method=['GET', 'POST'])
@role('lector')    
def edit(group_id):
    """Úprava specifické skupiny včetně přidávání uživatelů"""
    
    #todo: is allowed
    
    group = Group.get( group_id )
    
    # vložení studenta
    if request.forms.get("add"):
        try:
            usr = User.insert( request.forms.get("add"), group_id )
            msg("Student %s vložen" % usr.login,"success")
        except Exception as e: 
            msg("Chyba při vkládání studenta - %s " % e,"error")                   
                

        redirect(request.path)
    
    # odstranění studenta
    if request.query.get("remove"):
        usr = User.get( request.query.get("remove") )

        if not usr:
            msg("Student nenalezen","error")
        elif usr.remove():
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
    
@route('/groups/delete/<group_id:int>', method=['GET', 'POST'])
def delete(group_id):
    """Smaže skupinu"""

    group = Group.get( group_id )

    answer = request.forms.get("answer") 
    if answer:
        if answer == "Ne": redirect("/groups")
        if answer == "Ano":
            group.remove()
            msg("Skupina smazána","success")
            redirect("/groups")
            
    return template("question", {"question":"Skutečně chcete smazat skupinu '%s'" % group.name } )            
    
###############################################################################
# callbacky

@hook("before_request")
def groupMenu():
    usr = getUser() 

    if usr and usr.inRole("lector"):
        addMenu("/groups","Skupiny",50)

